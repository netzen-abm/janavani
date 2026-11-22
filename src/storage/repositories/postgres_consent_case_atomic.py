"""PostgreSQL transaction boundary for consent grants and Case audit events."""
from __future__ import annotations

import json
from typing import Any, Callable

from src.core.consent import Consent
from src.core.civic_case import CaseEvent, CaseEventType, CivicCase
from src.storage.postgres_unit_of_work import bind_postgres_principal, postgres_unit_of_work_factory
from src.storage.repositories.consent_case_atomic import ConsentIdempotencyConflictError
from src.storage.repositories.postgres_consent import PostgresConsentRepository
from src.storage.unit_of_work import UnitOfWorkFactory


class PostgresConsentCaseAtomicRepository:
    """Commit a consent grant and its Case event in one owner-scoped transaction."""

    def __init__(
        self, connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None, unit_of_work_factory: UnitOfWorkFactory | None = None,
        principal_id: str | None = None,
    ) -> None:
        self._connection_factory = connection_factory
        self._dsn = dsn
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

    @staticmethod
    def _select_action(cur, principal_id: str, fingerprint: str):
        cur.execute(
            """SELECT consent_id, subject_id, purpose, scope, grant_type, status,
                      created_at, expires_at, revoked_at, proof_ref, case_id
                 FROM civic_case_consents
                WHERE subject_id=%s AND action_fingerprint=%s
                FOR UPDATE""",
            (principal_id, fingerprint),
        )
        row = cur.fetchone()
        return (PostgresConsentRepository._hydrate(row[:10]), row[10]) if row else (None, None)

    @staticmethod
    def _matches(existing: Consent, incoming: Consent, case_id: str, existing_case_id: str | None) -> bool:
        return (
            existing_case_id == case_id
            and existing.consent_id == incoming.consent_id
            and existing.subject_id == incoming.subject_id
            and existing.purpose == incoming.purpose
            and existing.scope == incoming.scope
            and existing.grant_type is incoming.grant_type
            and existing.status is incoming.status
            and existing.expires_at == incoming.expires_at
            and existing.revoked_at == incoming.revoked_at
            and existing.proof_ref == incoming.proof_ref
        )

    @staticmethod
    def _verify_event(cur, consent: Consent, case_id: str, principal_id: str) -> None:
        cur.execute(
            """SELECT event_type, actor_id, source_ref, notes
                 FROM civic_case_events WHERE event_id=%s AND case_id=%s""",
            (f"consent-{consent.consent_id}", case_id),
        )
        row = cur.fetchone()
        if row is None or row != (
            CaseEventType.CONSENT_RECORDED.value, principal_id,
            consent.proof_ref, consent.purpose,
        ):
            raise RuntimeError("Existing consent action has no matching immutable Case event")

    def save_consent_and_case(
        self,
        consent: Consent,
        case: CivicCase,
        *,
        principal_id: str,
        action_fingerprint: str | None = None,
    ) -> Consent:
        if not isinstance(principal_id, str) or not principal_id.strip():
            raise ValueError("principal_id is required")
        if consent.subject_id != principal_id or case.created_by != principal_id:
            raise PermissionError("Consent and Case must belong to the transaction principal")
        if consent.consent_id not in case.consent_refs:
            raise ValueError("Case must reference consent before atomic persistence")

        event_id = f"consent-{consent.consent_id}"
        with self._unit_of_work_factory() as uow:
            conn = uow.connection
            bind_postgres_principal(conn, principal_id)
            with conn.cursor() as cur:
                if action_fingerprint:
                    existing, existing_case_id = self._select_action(
                        cur, principal_id, action_fingerprint
                    )
                    if existing is not None:
                        if not self._matches(existing, consent, case.case_id, existing_case_id):
                            raise ConsentIdempotencyConflictError(
                                "Consent action key was reused with different content"
                            )
                        self._verify_event(cur, existing, case.case_id, principal_id)
                        return existing

                cur.execute(
                    "SELECT created_by, version FROM civic_cases WHERE case_id=%s FOR UPDATE",
                    (case.case_id,),
                )
                current = cur.fetchone()
                if current is None:
                    raise LookupError("Case not found")
                if current[0] != principal_id:
                    raise PermissionError("Case owner does not match transaction principal")
                current_version = int(current[1])
                if case.version != current_version:
                    raise RuntimeError(
                        f"Expected Case version {case.version}, found {current_version}"
                    )

                if action_fingerprint:
                    existing, existing_case_id = self._select_action(
                        cur, principal_id, action_fingerprint
                    )
                    if existing is not None:
                        if not self._matches(existing, consent, case.case_id, existing_case_id):
                            raise ConsentIdempotencyConflictError(
                                "Consent action key was reused with different content"
                            )
                        self._verify_event(cur, existing, case.case_id, principal_id)
                        return existing
                    cur.execute(
                        """INSERT INTO civic_case_consents (
                            consent_id, case_id, purpose, scope, grant_type, status,
                            granted_by, subject_id, created_at, expires_at, revoked_at,
                            proof_ref, action_fingerprint
                        ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT DO NOTHING RETURNING consent_id""",
                        (consent.consent_id, case.case_id, consent.purpose,
                         json.dumps(list(consent.scope)), consent.grant_type.value,
                         consent.status.value, principal_id, consent.subject_id,
                         consent.created_at, consent.expires_at, consent.revoked_at,
                         consent.proof_ref, action_fingerprint),
                    )
                    inserted = cur.fetchone()
                    if inserted is None:
                        existing, existing_case_id = self._select_action(
                            cur, principal_id, action_fingerprint
                        )
                        if existing is None or not self._matches(
                            existing, consent, case.case_id, existing_case_id
                        ):
                            raise ConsentIdempotencyConflictError(
                                "Consent action identifier conflicts with another persisted grant"
                            )
                        self._verify_event(cur, existing, case.case_id, principal_id)
                        return existing
                else:
                    cur.execute(
                        """SELECT consent_id, subject_id, purpose, scope, grant_type,
                                  status, created_at, expires_at, revoked_at, proof_ref, case_id
                             FROM civic_case_consents WHERE consent_id=%s FOR UPDATE""",
                        (consent.consent_id,),
                    )
                    row = cur.fetchone()
                    if row is not None:
                        existing = PostgresConsentRepository._hydrate(row[:10])
                        if not self._matches(existing, consent, case.case_id, row[10]):
                            raise PermissionError("Persisted consent does not match this Case")
                    else:
                        cur.execute(
                            """INSERT INTO civic_case_consents (
                                consent_id, case_id, purpose, scope, grant_type, status,
                                granted_by, subject_id, created_at, expires_at, revoked_at, proof_ref
                            ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (consent.consent_id, case.case_id, consent.purpose,
                             json.dumps(list(consent.scope)), consent.grant_type.value,
                             consent.status.value, principal_id, consent.subject_id,
                             consent.created_at, consent.expires_at, consent.revoked_at,
                             consent.proof_ref),
                        )

                cur.execute(
                    "SELECT event_type, actor_id, source_ref, notes FROM civic_case_events "
                    "WHERE event_id=%s AND case_id=%s",
                    (event_id, case.case_id),
                )
                existing_event = cur.fetchone()
                if existing_event is not None:
                    if existing_event != (
                        CaseEventType.CONSENT_RECORDED.value, principal_id,
                        consent.proof_ref, consent.purpose,
                    ):
                        raise RuntimeError("Existing consent event conflicts with its grant")
                    return consent

                new_version = current_version + 1
                cur.execute(
                    """UPDATE civic_cases SET status=%s, updated_at=%s, version=%s
                       WHERE case_id=%s AND version=%s""",
                    (case.status.value, case.updated_at, new_version,
                     case.case_id, current_version),
                )
                if cur.rowcount != 1:
                    raise RuntimeError("Case optimistic concurrency check failed")
                cur.execute(
                    """INSERT INTO civic_case_events (
                        event_id, case_id, event_type, occurred_at, actor_id,
                        source_channel, source_ref, notes, event_version, created_at
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (event_id, case.case_id, CaseEventType.CONSENT_RECORDED.value,
                     consent.created_at, principal_id, None, consent.proof_ref,
                     consent.purpose, new_version, consent.created_at),
                )

        case.events.append(CaseEvent(
            event_id=event_id, case_id=case.case_id,
            event_type=CaseEventType.CONSENT_RECORDED,
            occurred_at=consent.created_at, actor_id=principal_id,
            source_ref=consent.proof_ref, notes=consent.purpose,
        ))
        case.version = new_version
        return consent
