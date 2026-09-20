"""PostgreSQL implementation of atomic consent + Case persistence."""
from __future__ import annotations

from typing import Any, Callable

from src.core.consent import Consent
from src.core.civic_case import CivicCase
from src.storage.postgres_unit_of_work import bind_postgres_principal, postgres_unit_of_work_factory
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
        self,
        consent: Consent,
        case: CivicCase,
        *,
        principal_id: str,
    ) -> None:
        if not principal_id.strip():
            raise ValueError("principal_id is required")
        if consent.subject_id != principal_id:
            raise PermissionError("Consent subject must match transaction principal")
        if consent.consent_id not in case.consent_refs:
            raise ValueError("Case must reference the consent before atomic persistence")
        with self._unit_of_work_factory() as uow:
            conn = uow.connection
            bind_postgres_principal(conn, principal_id)
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO civic_case_consents (
                        consent_id, case_id, purpose, scope, grant_type, status,
                        granted_by, subject_id, created_at, expires_at, revoked_at, proof_ref
                    ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (consent_id) DO UPDATE SET
                        case_id=EXCLUDED.case_id,
                        purpose=EXCLUDED.purpose,
                        scope=EXCLUDED.scope,
                        grant_type=EXCLUDED.grant_type,
                        status=EXCLUDED.status,
                        granted_by=EXCLUDED.granted_by,
                        subject_id=EXCLUDED.subject_id,
                        created_at=EXCLUDED.created_at,
                        expires_at=EXCLUDED.expires_at,
                        revoked_at=EXCLUDED.revoked_at,
                        proof_ref=EXCLUDED.proof_ref""",
                    (
                        consent.consent_id,
                        case.case_id,
                        consent.purpose,
                        __import__("json").dumps(list(consent.scope)),
                        consent.grant_type.value,
                        consent.status.value,
                        principal_id,
                        consent.subject_id,
                        consent.created_at,
                        consent.expires_at,
                        consent.revoked_at,
                        consent.proof_ref,
                    ),
                )
                # Case projection update is intentionally delegated through the
                # same transaction rather than calling a second repository/UoW.
                cur.execute(
                    """SELECT version FROM civic_cases
                       WHERE case_id=%s FOR UPDATE""",
                    (case.case_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise LookupError("Case not found")
                current_version = int(row[0])
                if case.version != current_version:
                    raise RuntimeError(
                        f"Expected Case version {case.version}, found {current_version}"
                    )
                new_version = current_version + 1
                cur.execute(
                    """UPDATE civic_cases
                       SET status=%s, updated_at=%s, version=%s
                       WHERE case_id=%s AND version=%s""",
                    (
                        case.status.value,
                        case.updated_at,
                        new_version,
                        case.case_id,
                        current_version,
                    ),
                )
                if cur.rowcount != 1:
                    raise RuntimeError("Case optimistic concurrency check failed")
                cur.execute(
                    """INSERT INTO civic_case_events (
                        event_id, case_id, event_type, occurred_at, actor_id,
                        source_channel, source_ref, notes, event_version, created_at
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        f"consent-{consent.consent_id}",
                        case.case_id,
                        "CONSENT_RECORDED",
                        consent.created_at,
                        principal_id,
                        None,
                        consent.proof_ref,
                        consent.purpose,
                        new_version,
                        consent.created_at,
                    ),
                )
        case.version = new_version
