"""Canonical PostgreSQL transaction boundary for Civic Case mutations.

This module is deliberately provider-neutral at its public contract while
using the shared PostgreSQL Unit of Work underneath. It does not activate RLS,
Supabase-specific authorization, or external submission semantics.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from src.core.civic_case import CaseEvent, CivicCase
from src.storage.postgres_unit_of_work import postgres_unit_of_work_factory
from src.storage.unit_of_work import UnitOfWorkFactory


class CaseTransactionError(RuntimeError):
    """Base error for the canonical case transaction boundary."""


class CaseTransactionConcurrencyError(CaseTransactionError):
    """The supplied expected version is stale."""


class CaseTransactionIdempotencyConflictError(CaseTransactionError):
    """An event/idempotency key was already used with a different payload."""


@dataclass(frozen=True)
class CaseMutationResult:
    """Deterministic result returned by an atomic case mutation."""

    case_id: str
    version: int
    event_id: str
    idempotent_replay: bool = False


def _event_payload(event: CaseEvent) -> tuple[Any, ...]:
    return (
        event.case_id,
        event.event_type.value,
        event.occurred_at,
        event.actor_id,
        event.source_channel,
        event.source_ref,
        event.notes,
    )


def _json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


class PostgresCaseTransactionRepository:
    """Persist one Case projection and one lifecycle event atomically.

    The operation is intentionally narrower than the full CivicCase
    repository: it provides the canonical mutation boundary needed by callers
    that already performed identity, authorization, consent, and lifecycle
    validation.
    """

    def __init__(
        self,
        connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None,
        unit_of_work_factory: UnitOfWorkFactory | None = None,
    ) -> None:
        self._dsn = dsn
        self._connection_factory = connection_factory
        if self._connection_factory is None and not self._dsn:
            raise ValueError("Provide connection_factory or dsn")
        self._unit_of_work_factory = unit_of_work_factory or postgres_unit_of_work_factory(
            self._connect
        )

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg

        return psycopg.connect(self._dsn)

    def persist_mutation(
        self,
        *,
        case: CivicCase,
        event: CaseEvent,
        expected_version: int,
        idempotency_key: str,
    ) -> CaseMutationResult:
        """Atomically persist a projection change and lifecycle event.

        ``event_id`` is the durable idempotency key. Replaying the exact same
        event returns the already committed version. Reusing the key with a
        different event payload fails. Existing cases use optimistic locking;
        creation starts at version 1.
        """
        if not idempotency_key or idempotency_key != event.event_id:
            raise CaseTransactionError("idempotency_key must equal event.event_id")
        if event.case_id != case.case_id:
            raise CaseTransactionError("event and case must have the same case_id")
        if expected_version < 0:
            raise CaseTransactionError("expected_version cannot be negative")

        with self._unit_of_work_factory() as uow:
            conn = uow.resource
            with conn.cursor(row_factory=self._row_factory()) as cur:
                cur.execute(
                    "SELECT * FROM civic_cases WHERE case_id = %s FOR UPDATE",
                    (case.case_id,),
                )
                current = cur.fetchone()

                cur.execute(
                    """SELECT event_id, case_id, event_type, occurred_at,
                              actor_id, source_channel, source_ref, notes
                       FROM civic_case_events WHERE event_id = %s""",
                    (idempotency_key,),
                )
                existing_event = cur.fetchone()
                if existing_event is not None:
                    existing_payload = tuple(
                        existing_event[key]
                        for key in (
                            "case_id", "event_type", "occurred_at", "actor_id",
                            "source_channel", "source_ref", "notes",
                        )
                    )
                    if existing_payload != _event_payload(event):
                        raise CaseTransactionIdempotencyConflictError(
                            f"Idempotency key {idempotency_key} has a different payload"
                        )
                    if current is None:
                        raise CaseTransactionError(
                            "Committed event exists without its case projection"
                        )
                    return CaseMutationResult(
                        case_id=case.case_id,
                        version=int(current["version"]),
                        event_id=event.event_id,
                        idempotent_replay=True,
                    )

                if current is None:
                    if expected_version != 0:
                        raise CaseTransactionConcurrencyError(
                            f"Expected version 0 for new case {case.case_id}"
                        )
                    now = case.updated_at or event.occurred_at
                    created_at = case.created_at or now
                    cur.execute(
                        """INSERT INTO civic_cases (
                            case_id, case_type, subject, narrative, created_by,
                            jurisdiction_json, related_organisation_id,
                            related_office_id, related_official_id,
                            related_representative_id, subject_claims_json,
                            status, created_at, updated_at, version
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s,
                            %s, %s::jsonb, %s, %s, %s, 1
                        )""",
                        (
                            case.case_id, case.case_type.value, case.subject,
                            case.narrative, case.created_by,
                            _json(case.jurisdiction), case.related_organisation_id,
                            case.related_office_id, case.related_official_id,
                            case.related_representative_id, _json(case.claims),
                            case.status.value, created_at, now,
                        ),
                    )
                    new_version = 1
                else:
                    current_version = int(current["version"])
                    if expected_version != current_version:
                        raise CaseTransactionConcurrencyError(
                            f"Expected version {expected_version}, found "
                            f"{current_version} for {case.case_id}"
                        )
                    new_version = current_version + 1
                    cur.execute(
                        """UPDATE civic_cases SET
                            case_type = %s, subject = %s, narrative = %s,
                            created_by = %s, jurisdiction_json = %s::jsonb,
                            related_organisation_id = %s, related_office_id = %s,
                            related_official_id = %s, related_representative_id = %s,
                            subject_claims_json = %s::jsonb, status = %s,
                            updated_at = %s, version = %s
                           WHERE case_id = %s AND version = %s""",
                        (
                            case.case_type.value, case.subject, case.narrative,
                            case.created_by, _json(case.jurisdiction),
                            case.related_organisation_id, case.related_office_id,
                            case.related_official_id, case.related_representative_id,
                            _json(case.claims), case.status.value,
                            event.occurred_at, new_version, case.case_id,
                            current_version,
                        ),
                    )
                    if cur.rowcount != 1:
                        raise CaseTransactionConcurrencyError(
                            f"Stale version for {case.case_id}"
                        )

                cur.execute(
                    """INSERT INTO civic_case_events (
                        event_id, case_id, event_type, occurred_at, actor_id,
                        source_channel, source_ref, notes, event_version, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        event.event_id, event.case_id, event.event_type.value,
                        event.occurred_at, event.actor_id, event.source_channel,
                        event.source_ref, event.notes, new_version, event.occurred_at,
                    ),
                )

        case.version = new_version
        case.created_at = case.created_at or event.occurred_at
        case.updated_at = event.occurred_at
        return CaseMutationResult(case.case_id, new_version, event.event_id)

    @staticmethod
    def _row_factory() -> Any:
        try:
            from psycopg.rows import dict_row
        except ImportError:
            return None
        return dict_row
