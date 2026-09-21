"""Canonical PostgreSQL transaction boundary for Civic Case mutations."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from src.core.civic_case import CaseEvent, CivicCase
from src.storage.postgres_unit_of_work import postgres_unit_of_work_factory
from src.storage.repositories.postgres_case_transaction_sql import (
    event_payload, find_event, insert_case, insert_event, lock_case, update_case,
)
from src.storage.unit_of_work import UnitOfWorkFactory

class CaseTransactionError(RuntimeError): pass
class CaseTransactionConcurrencyError(CaseTransactionError): pass
class CaseTransactionIdempotencyConflictError(CaseTransactionError): pass

@dataclass(frozen=True)
class CaseMutationResult:
    case_id: str
    version: int
    event_id: str
    idempotent_replay: bool = False

class PostgresCaseTransactionRepository:
    """Persist one Case projection and lifecycle event atomically."""
    def __init__(
        self, connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None, unit_of_work_factory: UnitOfWorkFactory | None = None,
        principal_id: str | None = None,
    ):
        self._dsn, self._connection_factory = dsn, connection_factory
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
        self, *, case: CivicCase, event: CaseEvent, expected_version: int,
        idempotency_key: str,
    ):
        self._validate(case, event, expected_version, idempotency_key)
        with self._unit_of_work_factory() as uow:
            with uow.resource.cursor(row_factory=self._row_factory()) as cur:
                current = lock_case(cur, case.case_id)
                existing = find_event(cur, idempotency_key)
                replay = self._replay(existing, current, case, event)
                if replay is not None:
                    return replay
                new_version = self._persist_case(cur, current, case, event, expected_version)
                insert_event(cur, event, new_version)
        case.version = new_version
        case.created_at = case.created_at or event.occurred_at
        case.updated_at = event.occurred_at
        return CaseMutationResult(case.case_id, new_version, event.event_id)

    @staticmethod
    def _validate(case, event, expected_version, idempotency_key):
        if not idempotency_key or idempotency_key != event.event_id:
            raise CaseTransactionError("idempotency_key must equal event.event_id")
        if event.case_id != case.case_id:
            raise CaseTransactionError("event and case must have the same case_id")
        if expected_version < 0:
            raise CaseTransactionError("expected_version cannot be negative")

    @staticmethod
    def _replay(existing, current, case, event):
        if existing is None:
            return None
        if tuple(existing[k] for k in (
            "case_id", "event_type", "occurred_at", "actor_id",
            "source_channel", "source_ref", "notes"
        )) != event_payload(event):
            raise CaseTransactionIdempotencyConflictError(
                f"Idempotency key {event.event_id} has a different payload"
            )
        if current is None:
            raise CaseTransactionError("Committed event exists without its case projection")
        return CaseMutationResult(
            case_id=case.case_id, version=int(current["version"]),
            event_id=event.event_id, idempotent_replay=True,
        )

    @staticmethod
    def _persist_case(cur, current, case, event, expected_version):
        if current is None:
            if expected_version != 0:
                raise CaseTransactionConcurrencyError(
                    f"Expected version 0 for new case {case.case_id}"
                )
            insert_case(cur, case, case.created_at or event.occurred_at,
                        case.updated_at or event.occurred_at)
            return 1
        current_version = int(current["version"])
        if expected_version != current_version:
            raise CaseTransactionConcurrencyError(
                f"Expected version {expected_version}, found {current_version} for {case.case_id}"
            )
        new_version = update_case(cur, case, event, current_version)
        if cur.rowcount != 1:
            raise CaseTransactionConcurrencyError(f"Stale version for {case.case_id}")
        return new_version

    @staticmethod
    def _row_factory():
        try:
            from psycopg.rows import dict_row
        except ImportError:
            return None
