"""Portable PostgreSQL provider for verified authority metadata."""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from src.core.authority import AuthorityContact, AuthorityRecord


class PostgresAuthorityRepository:
    """PostgreSQL authority directory provider behind the canonical contract."""

    def __init__(
        self,
        *,
        connection_factory: Callable[[], Any] | None = None,
        dsn: str | None = None,
    ) -> None:
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
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS civic_authorities (
                        authority_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        authority_type TEXT NOT NULL,
                        jurisdiction JSONB NOT NULL DEFAULT '{}'::jsonb,
                        primary_contact JSONB,
                        cc_contacts JSONB NOT NULL DEFAULT '[]'::jsonb,
                        source_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
                        verification_status TEXT NOT NULL,
                        last_verified_at TEXT
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS civic_authorities_type_city_idx
                    ON civic_authorities (authority_type)
                    """
                )

    def save(self, record: AuthorityRecord) -> None:
        primary_contact = (
            self._contact_dict(record.primary_contact)
            if record.primary_contact is not None
            else None
        )
        cc_contacts = [self._contact_dict(contact) for contact in record.cc_contacts]
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO civic_authorities (
                            authority_id, name, authority_type, jurisdiction,
                            primary_contact, cc_contacts, source_refs,
                            verification_status, last_verified_at
                        ) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb,
                                  %s::jsonb, %s, %s)
                        ON CONFLICT (authority_id) DO UPDATE SET
                            name=EXCLUDED.name,
                            authority_type=EXCLUDED.authority_type,
                            jurisdiction=EXCLUDED.jurisdiction,
                            primary_contact=EXCLUDED.primary_contact,
                            cc_contacts=EXCLUDED.cc_contacts,
                            source_refs=EXCLUDED.source_refs,
                            verification_status=EXCLUDED.verification_status,
                            last_verified_at=EXCLUDED.last_verified_at
                        """,
                        (
                            record.authority_id,
                            record.name,
                            record.authority_type,
                            json.dumps(record.jurisdiction),
                            json.dumps(primary_contact) if primary_contact else None,
                            json.dumps(cc_contacts),
                            json.dumps(record.source_refs),
                            record.verification_status,
                            record.last_verified_at,
                        ),
                    )

    def get(self, authority_id: str) -> AuthorityRecord | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT authority_id, name, authority_type, jurisdiction, "
                    "primary_contact, cc_contacts, source_refs, "
                    "verification_status, last_verified_at "
                    "FROM civic_authorities WHERE authority_id = %s",
                    (authority_id,),
                )
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    def search(
        self,
        *,
        authority_type: str,
        city: str,
        limit: int = 5,
    ) -> list[AuthorityRecord]:
        if limit < 1:
            return []
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT authority_id, name, authority_type, jurisdiction, "
                    "primary_contact, cc_contacts, source_refs, "
                    "verification_status, last_verified_at "
                    "FROM civic_authorities "
                    "WHERE LOWER(authority_type) LIKE %s "
                    "AND LOWER(COALESCE(jurisdiction->>'city', '')) LIKE %s "
                    "ORDER BY name LIMIT %s",
                    (f"%{authority_type.strip().lower()}%", f"%{city.strip().lower()}%", limit),
                )
                rows = cursor.fetchall()
        return [self._hydrate(row) for row in rows]

    @staticmethod
    def _contact_dict(contact: AuthorityContact) -> dict[str, Any]:
        return {
            "name": contact.name,
            "address": contact.address,
            "email": contact.email,
            "role": contact.role,
            "source_ref": contact.source_ref,
            "verified": contact.verified,
        }

    @staticmethod
    def _json_value(value: Any) -> Any:
        if isinstance(value, str):
            return json.loads(value)
        return value

    @classmethod
    def _hydrate(cls, row: Any) -> AuthorityRecord:
        jurisdiction = cls._json_value(row[3]) or {}
        primary = cls._json_value(row[4])
        cc_contacts = cls._json_value(row[5]) or []
        source_refs = cls._json_value(row[6]) or []
        return AuthorityRecord(
            authority_id=row[0],
            name=row[1],
            authority_type=row[2],
            jurisdiction=dict(jurisdiction),
            primary_contact=AuthorityContact(**primary) if primary else None,
            cc_contacts=tuple(AuthorityContact(**contact) for contact in cc_contacts),
            source_refs=tuple(source_refs),
            verification_status=row[7],
            last_verified_at=row[8],
        )
