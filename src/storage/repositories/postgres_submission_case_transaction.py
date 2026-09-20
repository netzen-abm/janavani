"""PostgreSQL implementation of the atomic Submission + Case boundary."""
from __future__ import annotations

import json
from typing import Any, Callable

from src.core.civic_case import CaseEvent, CivicCase
from src.core.submission import SubmissionRecord
from src.storage.postgres_unit_of_work import postgres_unit_of_work_factory
from src.storage.repositories.submission_case_transaction import (
    SubmissionCaseConcurrencyError,
    SubmissionCaseIdempotencyConflictError,
    SubmissionCaseMutationResult,
)
from src.storage.unit_of_work import UnitOfWorkFactory


class PostgresSubmissionCaseTransactionRepository:
    """Commit a coupled Submission mutation and Case lifecycle event atomically."""

    _SUBMISSION_SELECT = (
        "submission_id, case_id, destination_ref, document_ref, channel, state, "
        "attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref, "
        "error_code, retry_count, version, created_at, updated_at, idempotency_key"
    )

    def __init__(
        self,
        connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None,
        unit_of_work_factory: UnitOfWorkFactory | None = None,
        principal_id: str | None = None,
    ) -> None:
        self._connection_factory = connection_factory
        self._dsn = dsn
        self._principal_id = principal_id
        if connection_factory is None and not dsn:
            raise ValueError("Provide connection_factory or dsn")
        self._unit_of_work_factory = unit_of_work_factory or postgres_unit_of_work_factory(self._connect, principal_id=principal_id)

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    def persist_mutation(
        self,
        *,
        submission: SubmissionRecord,
        expected_submission_version: int,
        case: CivicCase,
        expected_case_version: int,
        event: CaseEvent,
        idempotency_key: str,
    ) -> SubmissionCaseMutationResult:
        if not idempotency_key or idempotency_key != event.event_id:
            raise ValueError("idempotency_key must equal event.event_id")
        if submission.case_id != case.case_id or event.case_id != case.case_id:
            raise ValueError("Submission, Case and event must reference the same case")
        if submission.version != expected_submission_version + 1:
            raise ValueError("Submission mutation must increment version by exactly one")
        if expected_case_version < 0:
            raise ValueError("expected_case_version cannot be negative")

        with self._unit_of_work_factory() as uow:
            conn = uow.resource
            with conn.cursor(row_factory=self._row_factory()) as cur:
                cur.execute(
                    "SELECT version FROM civic_cases WHERE case_id = %s FOR UPDATE",
                    (case.case_id,),
                )
                case_row = cur.fetchone()
                cur.execute(
                    "SELECT version, idempotency_key FROM civic_case_submissions WHERE submission_id = %s FOR UPDATE",
                    (submission.submission_id,),
                )
                submission_row = cur.fetchone()
                cur.execute(
                    "SELECT event_id, case_id, event_type, occurred_at, actor_id, source_channel, source_ref, notes "
                    "FROM civic_case_events WHERE event_id = %s",
                    (idempotency_key,),
                )
                existing_event = cur.fetchone()

                if existing_event is not None:
                    if existing_event["case_id"] != event.case_id or existing_event["event_type"] != event.event_type.value:
                        raise SubmissionCaseIdempotencyConflictError("Idempotency key is bound to a different lifecycle event")
                    if case_row is None or submission_row is None:
                        raise SubmissionCaseIdempotencyConflictError("Committed event is missing a coupled projection")
                    return SubmissionCaseMutationResult(
                        submission_id=submission.submission_id,
                        submission_version=int(submission_row["version"]),
                        case_id=case.case_id,
                        case_version=int(case_row["version"]),
                        event_id=event.event_id,
                        idempotent_replay=True,
                    )

                if case_row is None:
                    if expected_case_version != 0:
                        raise SubmissionCaseConcurrencyError("Expected Case version 0 for a new Case")
                    cur.execute(
                        """INSERT INTO civic_cases (
                            case_id, case_type, subject, narrative, created_by,
                            jurisdiction_json, related_organisation_id, related_office_id,
                            related_official_id, related_representative_id, subject_claims_json,
                            status, created_at, updated_at, version
                        ) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,1)""",
                        (
                            case.case_id, case.case_type.value, case.subject, case.narrative, case.created_by,
                            json.dumps(case.jurisdiction, ensure_ascii=False, separators=(",", ":")),
                            case.related_organisation_id, case.related_office_id, case.related_official_id,
                            case.related_representative_id, json.dumps(case.claims, ensure_ascii=False, separators=(",", ":")),
                            case.status.value, case.created_at or event.occurred_at, case.updated_at or event.occurred_at,
                        ),
                    )
                    case_version = 1
                else:
                    current_case_version = int(case_row["version"])
                    if current_case_version != expected_case_version:
                        raise SubmissionCaseConcurrencyError(
                            f"Case version mismatch: expected {expected_case_version}, found {current_case_version}"
                        )
                    case_version = current_case_version + 1
                    cur.execute(
                        """UPDATE civic_cases SET case_type=%s, subject=%s, narrative=%s, created_by=%s,
                            jurisdiction_json=%s::jsonb, related_organisation_id=%s, related_office_id=%s,
                            related_official_id=%s, related_representative_id=%s, subject_claims_json=%s::jsonb,
                            status=%s, updated_at=%s, version=%s WHERE case_id=%s AND version=%s""",
                        (
                            case.case_type.value, case.subject, case.narrative, case.created_by,
                            json.dumps(case.jurisdiction, ensure_ascii=False, separators=(",", ":")),
                            case.related_organisation_id, case.related_office_id, case.related_official_id,
                            case.related_representative_id, json.dumps(case.claims, ensure_ascii=False, separators=(",", ":")),
                            case.status.value, event.occurred_at, case_version, case.case_id, expected_case_version,
                        ),
                    )
                    if cur.rowcount != 1:
                        raise SubmissionCaseConcurrencyError("Case compare-and-swap failed")

                if submission_row is None:
                    if expected_submission_version != 0:
                        raise SubmissionCaseConcurrencyError("Expected Submission version 0 for a new Submission")
                    cur.execute(
                        f"""INSERT INTO civic_case_submissions (
                            submission_id, case_id, destination_ref, document_ref, channel, state,
                            attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref,
                            error_code, retry_count, version, created_at, updated_at, idempotency_key
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        self._submission_params(submission),
                    )
                    submission_version = submission.version
                else:
                    current_submission_version = int(submission_row["version"])
                    if current_submission_version != expected_submission_version:
                        raise SubmissionCaseConcurrencyError(
                            f"Submission version mismatch: expected {expected_submission_version}, found {current_submission_version}"
                        )
                    if submission_row["idempotency_key"] != submission.idempotency_key:
                        raise SubmissionCaseIdempotencyConflictError("Submission idempotency key is immutable")
                    cur.execute(
                        """UPDATE civic_case_submissions SET case_id=%s,destination_ref=%s,document_ref=%s,
                            channel=%s,state=%s,attempted_at=%s,submitted_at=%s,acknowledged_at=%s,
                            external_reference=%s,ack_ref=%s,error_code=%s,retry_count=%s,version=%s,
                            created_at=%s,updated_at=%s WHERE submission_id=%s AND version=%s""",
                        self._submission_update_params(submission, expected_submission_version),
                    )
                    if cur.rowcount != 1:
                        raise SubmissionCaseConcurrencyError("Submission compare-and-swap failed")
                    submission_version = submission.version

                cur.execute(
                    """INSERT INTO civic_case_events (
                        event_id, case_id, event_type, occurred_at, actor_id, source_channel,
                        source_ref, notes, event_version, created_at
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (event.event_id, event.case_id, event.event_type.value, event.occurred_at,
                     event.actor_id, event.source_channel, event.source_ref, event.notes,
                     case_version, event.occurred_at),
                )

        return SubmissionCaseMutationResult(
            submission_id=submission.submission_id,
            submission_version=submission_version,
            case_id=case.case_id,
            case_version=case_version,
            event_id=event.event_id,
        )

    @staticmethod
    def _submission_params(submission: SubmissionRecord) -> tuple[Any, ...]:
        return (
            submission.submission_id, submission.case_id, submission.destination_ref, submission.document_ref,
            submission.channel, submission.state, submission.attempted_at, submission.submitted_at,
            submission.acknowledged_at, submission.external_reference, submission.ack_ref, submission.error_code,
            submission.retry_count, submission.version, submission.created_at, submission.updated_at,
            submission.idempotency_key,
        )

    @staticmethod
    def _submission_update_params(submission: SubmissionRecord, expected_version: int) -> tuple[Any, ...]:
        return (
            submission.case_id, submission.destination_ref, submission.document_ref, submission.channel,
            submission.state, submission.attempted_at, submission.submitted_at, submission.acknowledged_at,
            submission.external_reference, submission.ack_ref, submission.error_code, submission.retry_count,
            submission.version, submission.created_at, submission.updated_at, submission.submission_id,
            expected_version,
        )

    @staticmethod
    def _row_factory() -> Any:
        try:
            from psycopg.rows import dict_row
        except ImportError:
            return None
        return dict_row
