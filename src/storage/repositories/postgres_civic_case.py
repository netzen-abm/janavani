"""Standard PostgreSQL provider for the canonical CivicCase repository.

This provider uses PostgreSQL directly through Psycopg 3. It does not depend
on Supabase, a hosted database, or an ORM. The domain contract remains the
same, so another PostgreSQL deployment can replace this provider unchanged.

The repository owns persistence mechanics only. Lifecycle validation,
identity, authorization, consent decisions, and submission semantics remain
outside the provider.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Callable

from src.core.civic_case import (
    CaseEvent,
    CaseEventType,
    CaseStatus,
    CaseType,
    CivicCase,
)
from src.storage.postgres_unit_of_work import postgres_unit_of_work_factory
from src.storage.unit_of_work import UnitOfWorkFactory


class PostgresCivicCasePersistenceError(RuntimeError):
    """Raised when PostgreSQL Civic Case persistence fails."""


class PostgresCivicCaseConcurrencyError(PostgresCivicCasePersistenceError):
    """Raised when optimistic concurrency detects a stale case version."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def _case_values(case: CivicCase, *, created_at: str,
                 updated_at: str, version: int) -> tuple[Any, ...]:
    return (
        case.case_id,
        case.case_type.value,
        case.subject,
        case.narrative,
        case.created_by,
        _json(case.jurisdiction),
        case.related_organisation_id,
        case.related_office_id,
        case.related_official_id,
        case.related_representative_id,
        _json(case.claims),
        case.status.value,
        created_at,
        updated_at,
        version,
    )


def _event_values(event: CaseEvent) -> tuple[Any, ...]:
    return (
        event.event_id,
        event.case_id,
        event.event_type.value,
        event.occurred_at,
        event.actor_id,
        event.source_channel,
        event.source_ref,
        event.notes,
        1,
        _now(),
    )


def _decode_json(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, str):
        return json.loads(value)
    return value


def _hydrate(row: dict[str, Any], events: list[dict[str, Any]],
             evidence: list[dict[str, Any]],
             documents: list[dict[str, Any]],
             consents: list[dict[str, Any]]) -> CivicCase:
    return CivicCase(
        case_id=str(row["case_id"]),
        case_type=CaseType(row["case_type"]),
        subject=str(row["subject"]),
        narrative=str(row["narrative"]),
        created_by=row.get("created_by"),
        jurisdiction=_decode_json(row.get("jurisdiction_json"), {}),
        related_organisation_id=row.get("related_organisation_id"),
        related_office_id=row.get("related_office_id"),
        related_official_id=row.get("related_official_id"),
        related_representative_id=row.get("related_representative_id"),
        claims=_decode_json(row.get("subject_claims_json"), []),
        evidence_refs=[str(item["evidence_id"]) for item in evidence],
        document_refs=[str(item["document_id"]) for item in documents],
        consent_refs=[str(item["consent_id"]) for item in consents],
        status=CaseStatus(row["status"]),
        events=[
            CaseEvent(
                event_id=str(item["event_id"]),
                case_id=str(item["case_id"]),
                event_type=CaseEventType(item["event_type"]),
                occurred_at=str(item["occurred_at"]),
                actor_id=item.get("actor_id"),
                source_channel=item.get("source_channel"),
                source_ref=item.get("source_ref"),
                notes=item.get("notes"),
            )
            for item in events
        ],
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        version=int(row.get("version", 1)),
    )


class PostgresCivicCaseRepository:
    """Atomic PostgreSQL implementation of ``CivicCaseRepository``.

    ``connection_factory`` is injected for tests and deployment freedom. When
    omitted, ``JANAVANI_POSTGRES_DSN`` is used with Psycopg 3. The provider
    does not import or initialize Supabase.

    ``unit_of_work_factory`` can be injected when this repository participates
    in a larger provider-owned transaction boundary. By default it is derived
    from this repository's connection factory, preserving standalone behavior.
    """

    def __init__(
        self,
        connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None,
        unit_of_work_factory: UnitOfWorkFactory | None = None,
    ) -> None:
        self._dsn = dsn or os.getenv("JANAVANI_POSTGRES_DSN")
        self._connection_factory = connection_factory
        if self._connection_factory is None and not self._dsn:
            raise ValueError(
                "Provide connection_factory or JANAVANI_POSTGRES_DSN"
            )
        self._unit_of_work_factory = unit_of_work_factory or (
            postgres_unit_of_work_factory(self._connect)
        )

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise PostgresCivicCasePersistenceError(
                "Psycopg 3 is required for the PostgreSQL provider"
            ) from exc
        return psycopg.connect(self._dsn)

    def get(self, case_id: str) -> CivicCase | None:
        try:
            with self._connect() as conn:
                with conn.cursor(row_factory=self._row_factory()) as cur:
                    cur.execute(
                        "SELECT * FROM civic_cases WHERE case_id = %s",
                        (case_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        return None
                    events = self._select_children(cur, "civic_case_events", case_id)
                    evidence = self._select_children(
                        cur, "civic_case_evidence_refs", case_id
                    )
                    documents = self._select_children(
                        cur, "civic_case_document_refs", case_id
                    )
                    consents = self._select_children(
                        cur, "civic_case_consents", case_id
                    )
                    return _hydrate(
                        row, events, evidence, documents, consents
                    )
        except PostgresCivicCasePersistenceError:
            raise
        except Exception as exc:
            raise PostgresCivicCasePersistenceError(
                f"Failed to read Civic Case {case_id}"
            ) from exc

    def save(self, case: CivicCase) -> None:
        try:
            with self._unit_of_work_factory() as uow:
                conn = uow.connection
                with conn.cursor(row_factory=self._row_factory()) as cur:
                    cur.execute(
                        "SELECT version, created_at "
                        "FROM civic_cases "
                        "WHERE case_id = %s FOR UPDATE",
                        (case.case_id,),
                    )
                    current = cur.fetchone()
                    now = _now()
                    if current is None:
                        persisted_version = 1
                        created_at = case.created_at or now
                        self._insert_case(
                            cur, case, created_at, now, persisted_version
                        )
                    else:
                        current_version = int(current["version"])
                        if case.version != current_version:
                            raise PostgresCivicCaseConcurrencyError(
                                f"Expected version {case.version}, "
                                f"found {current_version} for {case.case_id}"
                            )
                        persisted_version = current_version + 1
                        created_at = str(current["created_at"])
                        self._update_case(
                            cur,
                            case,
                            created_at,
                            now,
                            persisted_version,
                            current_version,
                        )

                    self._persist_events(cur, case)
                    self._persist_refs(cur, case)

            case.created_at = created_at
            case.updated_at = now
            case.version = persisted_version
        except (
            PostgresCivicCasePersistenceError,
            PostgresCivicCaseConcurrencyError,
        ):
            raise
        except Exception as exc:
            raise PostgresCivicCasePersistenceError(
                f"Failed to persist Civic Case {case.case_id}"
            ) from exc

    @staticmethod
    def _row_factory() -> Any:
        try:
            from psycopg.rows import dict_row
        except ImportError:
            return None
        return dict_row

    @staticmethod
    def _select_children(cur: Any, table: str,
                         case_id: str) -> list[dict[str, Any]]:
        order = ""
        if table == "civic_case_events":
            order = " ORDER BY occurred_at, event_id"
        cur.execute(
            f"SELECT * FROM {table} WHERE case_id = %s{order}",
            (case_id,),
        )
        return list(cur.fetchall())

    @staticmethod
    def _insert_case(cur: Any, case: CivicCase, created_at: str,
                     updated_at: str, version: int) -> None:
        cur.execute(
            """INSERT INTO civic_cases (
                case_id, case_type, subject, narrative, created_by,
                jurisdiction_json, related_organisation_id, related_office_id,
                related_official_id, related_representative_id,
                subject_claims_json, status, created_at, updated_at, version
            ) VALUES (
                %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s,
                %s::jsonb, %s, %s, %s, %s
            )""",
            _case_values(
                case,
                created_at=created_at,
                updated_at=updated_at,
                version=version,
            ),
        )

    @staticmethod
    def _update_case(cur: Any, case: CivicCase, created_at: str,
                     updated_at: str, version: int,
                     current_version: int) -> None:
        cur.execute(
            """UPDATE civic_cases SET
                case_type = %s,
                subject = %s,
                narrative = %s,
                created_by = %s,
                jurisdiction_json = %s::jsonb,
                related_organisation_id = %s,
                related_office_id = %s,
                related_official_id = %s,
                related_representative_id = %s,
                subject_claims_json = %s::jsonb,
                status = %s,
                created_at = %s,
                updated_at = %s,
                version = %s
            WHERE case_id = %s AND version = %s""",
            (
                case.case_type.value,
                case.subject,
                case.narrative,
                case.created_by,
                _json(case.jurisdiction),
                case.related_organisation_id,
                case.related_office_id,
                case.related_official_id,
                case.related_representative_id,
                _json(case.claims),
                case.status.value,
                created_at,
                updated_at,
                version,
                case.case_id,
                current_version,
            ),
        )
        if cur.rowcount != 1:
            raise PostgresCivicCaseConcurrencyError(
                f"Stale CivicCase version for {case.case_id}"
            )

    @staticmethod
    def _persist_events(cur: Any, case: CivicCase) -> None:
        cur.execute(
            "SELECT event_id FROM civic_case_events WHERE case_id = %s",
            (case.case_id,),
        )
        existing = {str(row["event_id"]) for row in cur.fetchall()}
        pending = [
            _event_values(event)
            for event in case.events
            if event.event_id not in existing
        ]
        if not pending:
            return
        cur.executemany(
            """INSERT INTO civic_case_events (
                event_id, case_id, event_type, occurred_at, actor_id,
                source_channel, source_ref, notes, event_version, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            pending,
        )

    @staticmethod
    def _persist_refs(cur: Any, case: CivicCase) -> None:
        if case.evidence_refs:
            cur.executemany(
                """INSERT INTO civic_case_evidence_refs (
                    case_id, evidence_id, relationship, created_at
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (case_id, evidence_id, relationship) DO NOTHING""",
                [
                    (case.case_id, evidence_id, "case_evidence", _now())
                    for evidence_id in case.evidence_refs
                ],
            )
        if case.document_refs:
            cur.executemany(
                """INSERT INTO civic_case_document_refs (
                    case_id, document_id, relationship, version, created_at
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (case_id, document_id, relationship) DO NOTHING""",
                [
                    (case.case_id, document_id, "case_document", 1, _now())
                    for document_id in case.document_refs
                ],
            )
