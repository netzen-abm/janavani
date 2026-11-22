"""PostgreSQL transaction boundary for consent grants and Case audit events."""
from __future__ import annotations

from typing import Any, Callable

from src.core.consent import Consent
from src.core.civic_case import CaseEvent, CaseEventType, CivicCase
from src.storage.postgres_unit_of_work import bind_postgres_principal, postgres_unit_of_work_factory
from src.storage.repositories.consent_case_atomic import ConsentIdempotencyConflictError
from src.storage.repositories.postgres_consent import PostgresConsentRepository
from src.storage.repositories.postgres_consent_case_atomic_sql import (
    attach_existing_consent_to_case, insert_action_consent, insert_attached_consent,
    insert_consent_event, lock_case, select_action, select_consent, select_event,
    update_case,
)
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
    def _select_action(cursor, principal_id: str, fingerprint: str):
        row = select_action(cursor, principal_id, fingerprint)
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
    def _verify_event(cursor, consent: Consent, case_id: str, principal_id: str) -> None:
        expected = (
            CaseEventType.CONSENT_RECORDED.value, principal_id,
            consent.proof_ref, consent.purpose,
        )
        if select_event(cursor, f"consent-{consent.consent_id}", case_id) != expected:
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
            with conn.cursor() as cursor:
                if action_fingerprint:
                    existing, existing_case_id = self._select_action(
                        cursor, principal_id, action_fingerprint
                    )
                    if existing is not None:
                        if not self._matches(existing, consent, case.case_id, existing_case_id):
                            raise ConsentIdempotencyConflictError(
                                "Consent action key was reused with different content"
                            )
                        self._verify_event(cursor, existing, case.case_id, principal_id)
                        return existing

                current = lock_case(cursor, case.case_id)
                if current is None:
                    raise LookupError("Case not found")
                if current[0] != principal_id:
                    raise PermissionError("Case owner does not match transaction principal")
                current_version = int(current[1])
                if action_fingerprint:
                    existing, existing_case_id = self._select_action(
                        cursor, principal_id, action_fingerprint
                    )
                    if existing is not None:
                        if not self._matches(existing, consent, case.case_id, existing_case_id):
                            raise ConsentIdempotencyConflictError(
                                "Consent action key was reused with different content"
                            )
                        self._verify_event(cursor, existing, case.case_id, principal_id)
                        return existing
                if case.version != current_version:
                    raise RuntimeError(
                        f"Expected Case version {case.version}, found {current_version}"
                    )

                if action_fingerprint:
                    inserted = insert_action_consent(
                        cursor, consent, case.case_id, principal_id, action_fingerprint
                    )
                    if inserted is None:
                        existing, existing_case_id = self._select_action(
                            cursor, principal_id, action_fingerprint
                        )
                        if existing is None or not self._matches(
                            existing, consent, case.case_id, existing_case_id
                        ):
                            raise ConsentIdempotencyConflictError(
                                "Consent action identifier conflicts with another persisted grant"
                            )
                        self._verify_event(cursor, existing, case.case_id, principal_id)
                        return existing
                else:
                    row = select_consent(cursor, consent.consent_id)
                    if row is not None:
                        existing = PostgresConsentRepository._hydrate(row[:10])
                        if row[10] not in (None, case.case_id) or not self._matches(
                            existing, consent, case.case_id, row[10] or case.case_id
                        ):
                            raise PermissionError("Persisted consent does not match this Case")
                        if row[10] is None:
                            attach_existing_consent_to_case(
                                cursor, consent.consent_id, case.case_id, principal_id
                            )
                    else:
                        insert_attached_consent(cursor, consent, case.case_id, principal_id)

                existing_event = select_event(cursor, event_id, case.case_id)
                expected_event = (
                    CaseEventType.CONSENT_RECORDED.value, principal_id,
                    consent.proof_ref, consent.purpose,
                )
                if existing_event is not None:
                    if existing_event != expected_event:
                        raise RuntimeError("Existing consent event conflicts with its grant")
                    return consent

                new_version = current_version + 1
                case.updated_at = consent.created_at
                update_case(cursor, case, current_version, new_version)
                if cursor.rowcount != 1:
                    raise RuntimeError("Case optimistic concurrency check failed")
                insert_consent_event(
                    cursor, event_id, case.case_id, consent, principal_id, new_version
                )

        case.events.append(CaseEvent(
            event_id=event_id, case_id=case.case_id,
            event_type=CaseEventType.CONSENT_RECORDED,
            occurred_at=consent.created_at, actor_id=principal_id,
            source_ref=consent.proof_ref, notes=consent.purpose,
        ))
        case.version = new_version
        return consent
