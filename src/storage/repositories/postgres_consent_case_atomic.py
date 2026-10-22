"""PostgreSQL implementation of atomic consent + Case persistence."""
from __future__ import annotations

import json
from typing import Any, Callable

from src.core.consent import Consent
from src.core.civic_case import CaseEvent, CaseEventType, CivicCase
from src.storage.postgres_unit_of_work import bind_postgres_principal, postgres_unit_of_work_factory
from src.storage.repositories.postgres_civic_case_codec import event_values, now
from src.storage.unit_of_work import UnitOfWorkFactory


class PostgresConsentCaseAtomicRepository:
    """Commit consent and its Case projection in one PostgreSQL transaction."""

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
        self._unit_of_work_factory = unit_of_work_factory or postgres_unit_of_work_factory(
            self._connect, principal_id=principal_id
        )

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    def save_consent_and_case(
        self, consent: Consent, case: CivicCase, *, principal_id: str
    ) -> None:
        if not principal_id.strip():
            raise ValueError("principal_id is required")
        if consent.subject_id != principal_id or case.created_by != principal_id:
            raise PermissionError("Consent subject and Case owner must match transaction principal")
        if consent.consent_id not in case.consent_refs:
            raise ValueError("Case must reference the consent before atomic persistence")
        new_version = None
        with self._unit_of_work_factory() as uow:
            conn = uow.connection
            bind_postgres_principal(conn, principal_id)
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT case_id, subject_id, purpose, scope, grant_type, status, proof_ref
                       FROM civic_case_consents WHERE consent_id=%s FOR UPDATE""",
                    (consent.consent_id,),
                )
                existing = cur.fetchone()
                if existing:
                    stored_scope = json.loads(existing[3]) if isinstance(existing[3], str) else existing[3]
                    if (existing[0], existing[1], existing[2], tuple(stored_scope),
                        existing[4], existing[5], existing[6]) != (
                        case.case_id, principal_id, consent.purpose, tuple(consent.scope),
                        consent.grant_type.value, consent.status.value, consent.proof_ref
                    ):
                        raise ValueError("Consent identifier is already bound to a different consent")
                cur.execute(
                    """SELECT version, status, created_by, updated_at FROM civic_cases
                       WHERE case_id=%s FOR UPDATE""",
                    (case.case_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise LookupError("Case not found")
                current_version, current_status, current_owner = int(row[0]), row[1], row[2]
                if current_owner != principal_id:
                    raise PermissionError("Case owner does not match transaction principal")
                consent_event_id = f"event-consent-00-recorded-{consent.consent_id}"
                if not any(event.event_id == consent_event_id for event in case.events):
                    case.events.append(CaseEvent(
                        event_id=consent_event_id, case_id=case.case_id,
                        event_type=CaseEventType.CONSENT_RECORDED,
                        occurred_at=consent.created_at, actor_id=principal_id,
                        source_ref=consent.proof_ref, notes=consent.purpose,
                    ))
                cur.execute("SELECT event_id FROM civic_case_events WHERE case_id=%s", (case.case_id,))
                existing_events = {str(event[0]) for event in cur.fetchall()}
                pending_events = [event_values(event) for event in case.events
                                  if event.event_id not in existing_events]
                # A retry after commit but before acknowledgement must not mutate the Case again.
                if existing and current_status == case.status.value and not pending_events:
                    case.version = current_version
                    return
                if case.version != current_version:
                    raise RuntimeError(
                        f"Expected Case version {case.version}, found {current_version}"
                    )
                cur.execute(
                    """INSERT INTO civic_case_consents (
                        consent_id, case_id, purpose, scope, grant_type, status,
                        granted_by, subject_id, created_at, expires_at, revoked_at, proof_ref
                    ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (consent_id) DO NOTHING""",
                    (consent.consent_id, case.case_id, consent.purpose,
                     json.dumps(list(consent.scope)), consent.grant_type.value,
                     consent.status.value, principal_id, consent.subject_id,
                     consent.created_at, consent.expires_at, consent.revoked_at,
                     consent.proof_ref),
                )
                new_version = current_version + 1
                updated_at = case.updated_at or now()
                cur.execute(
                    """UPDATE civic_cases SET status=%s, updated_at=%s, version=%s
                       WHERE case_id=%s AND version=%s""",
                    (case.status.value, updated_at, new_version, case.case_id, current_version),
                )
                if cur.rowcount != 1:
                    raise RuntimeError("Case optimistic concurrency check failed")
                if pending_events:
                    cur.executemany(
                        """INSERT INTO civic_case_events (
                            event_id, case_id, event_type, occurred_at, actor_id,
                            source_channel, source_ref, notes, event_version, created_at
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (event_id) DO NOTHING""",
                        pending_events,
                    )
        case.version = new_version
        case.updated_at = updated_at
