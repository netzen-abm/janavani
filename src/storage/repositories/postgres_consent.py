"""Portable PostgreSQL provider for explicit consent records."""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from src.core.consent import Consent, ConsentGrantType, ConsentStatus


class PostgresConsentRepository:
    """Durable consent provider independent of identity or transport."""

    def __init__(self, *, connection_factory: Callable[[], Any] | None = None, dsn: str | None = None) -> None:
        if connection_factory is None and not (dsn or os.getenv("JANAVANI_POSTGRES_DSN")):
            raise ValueError("PostgreSQL provider requires a DSN or connection factory")
        self._connection_factory = connection_factory
        self._dsn = dsn or os.getenv("JANAVANI_POSTGRES_DSN")
        self._initialize()

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    def _initialize(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS civic_case_consents (
                        consent_id TEXT PRIMARY KEY,
                        subject_id TEXT NOT NULL,
                        purpose TEXT NOT NULL,
                        scope JSONB NOT NULL,
                        grant_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        expires_at TIMESTAMPTZ,
                        revoked_at TIMESTAMPTZ,
                        proof_ref TEXT
                    )
                """)
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS civic_case_consents_subject_idx "
                    "ON civic_case_consents(subject_id, created_at)"
                )

    def save(self, consent: Consent) -> None:
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO civic_case_consents (
                            consent_id, subject_id, purpose, scope, grant_type,
                            status, created_at, expires_at, revoked_at, proof_ref
                        ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (consent_id) DO UPDATE SET
                            subject_id=EXCLUDED.subject_id,
                            purpose=EXCLUDED.purpose,
                            scope=EXCLUDED.scope,
                            grant_type=EXCLUDED.grant_type,
                            status=EXCLUDED.status,
                            created_at=EXCLUDED.created_at,
                            expires_at=EXCLUDED.expires_at,
                            revoked_at=EXCLUDED.revoked_at,
                            proof_ref=EXCLUDED.proof_ref
                    """, (
                        consent.consent_id, consent.subject_id, consent.purpose,
                        json.dumps(list(consent.scope)), consent.grant_type.value,
                        consent.status.value, consent.created_at,
                        consent.expires_at, consent.revoked_at, consent.proof_ref,
                    ))

    def get(self, consent_id: str) -> Consent | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT consent_id, subject_id, purpose, scope, grant_type, "
                    "status, created_at, expires_at, revoked_at, proof_ref "
                    "FROM civic_case_consents WHERE consent_id=%s",
                    (consent_id,),
                )
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    def list_for_subject(self, subject_id: str) -> list[Consent]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT consent_id, subject_id, purpose, scope, grant_type, "
                    "status, created_at, expires_at, revoked_at, proof_ref "
                    "FROM civic_case_consents WHERE subject_id=%s "
                    "ORDER BY created_at, consent_id",
                    (subject_id,),
                )
                rows = cursor.fetchall()
        return [self._hydrate(row) for row in rows]

    @staticmethod
    def _hydrate(row: Any) -> Consent:
        scope = row[3]
        if isinstance(scope, str):
            scope = json.loads(scope)
        return Consent(
            consent_id=row[0], subject_id=row[1], purpose=row[2],
            scope=tuple(scope), grant_type=ConsentGrantType(row[4]),
            status=ConsentStatus(row[5]), created_at=row[6],
            expires_at=row[7], revoked_at=row[8], proof_ref=row[9],
        )
