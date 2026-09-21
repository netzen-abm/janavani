"""PostgreSQL implementation of the atomic Submission + Case boundary."""
from __future__ import annotations
from typing import Any, Callable
from src.core.civic_case import CaseEvent, CivicCase
from src.core.submission import SubmissionRecord
from src.storage.postgres_unit_of_work import postgres_unit_of_work_factory
from src.storage.repositories.submission_case_transaction import (
    SubmissionCaseConcurrencyError, SubmissionCaseIdempotencyConflictError,
    SubmissionCaseMutationResult,
)
from src.storage.repositories.postgres_submission_case_transaction_sql import (
    lock_state, persist_case, persist_event, persist_submission,
)
from src.storage.unit_of_work import UnitOfWorkFactory

class PostgresSubmissionCaseTransactionRepository:
    """Commit coupled Submission + Case lifecycle mutation atomically."""

    def __init__(
        self, connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None, unit_of_work_factory: UnitOfWorkFactory | None = None,
        principal_id: str | None = None,
    ) -> None:
        self._connection_factory = connection_factory
        self._dsn = dsn
        self._principal_id = principal_id
        if connection_factory is None and not dsn:
            raise ValueError("Provide connection_factory or dsn")
        self._unit_of_work_factory = unit_of_work_factory or postgres_unit_of_work_factory(
            self._connect, principal_id=principal_id
        )

    def _connect(self):
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    def persist_mutation(
        self, *, submission: SubmissionRecord, expected_submission_version: int,
        case: CivicCase, expected_case_version: int, event: CaseEvent,
        idempotency_key: str,
    ) -> SubmissionCaseMutationResult:
        self._validate(
            submission, expected_submission_version, case,
            expected_case_version, event, idempotency_key
        )
        with self._unit_of_work_factory() as uow:
            with uow.resource.cursor(row_factory=self._row_factory()) as cur:
                state = lock_state(cur, case.case_id, submission.submission_id, idempotency_key)
                replay = self._replay(state, submission, case, event)
                if replay is not None:
                    return replay
                case_version = persist_case(
                    cur, case, expected_case_version, event
                )
                submission_version = persist_submission(
                    cur, submission, expected_submission_version
                )
                persist_event(cur, event, case_version)
        return SubmissionCaseMutationResult(
            submission_id=submission.submission_id,
            submission_version=submission_version,
            case_id=case.case_id,
            case_version=case_version,
            event_id=event.event_id,
        )

    @staticmethod
    def _validate(submission, expected_submission_version, case,
                  expected_case_version, event, idempotency_key):
        if not idempotency_key or idempotency_key != event.event_id:
            raise ValueError("idempotency_key must equal event.event_id")
        if submission.case_id != case.case_id or event.case_id != case.case_id:
            raise ValueError("Submission, Case and event must reference the same case")
        if submission.version != expected_submission_version + 1:
            raise ValueError("Submission mutation must increment version by exactly one")
        if expected_case_version < 0:
            raise ValueError("expected_case_version cannot be negative")

    @staticmethod
    def _replay(state, submission, case, event):
        existing_event, case_row, submission_row = state
        if existing_event is None:
            return None
        if (
            existing_event["case_id"] != event.case_id
            or existing_event["event_type"] != event.event_type.value
        ):
            raise SubmissionCaseIdempotencyConflictError(
                "Idempotency key is bound to a different lifecycle event"
            )
        if case_row is None or submission_row is None:
            raise SubmissionCaseIdempotencyConflictError(
                "Committed event is missing a coupled projection"
            )
        return SubmissionCaseMutationResult(
            submission_id=submission.submission_id,
            submission_version=int(submission_row["version"]),
            case_id=case.case_id,
            case_version=int(case_row["version"]),
            event_id=event.event_id,
            idempotent_replay=True,
        )

    @staticmethod
    def _row_factory():
        try:
            from psycopg.rows import dict_row
        except ImportError:
            return None
        return dict_row
