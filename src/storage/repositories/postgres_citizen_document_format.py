"""PostgreSQL persistence for owner-scoped, content-free document formats."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Callable

from src.documents.citizen_document_format import CitizenDocumentFormat
from src.storage.postgres_unit_of_work import bind_postgres_principal


class PostgresCitizenDocumentFormatRepository:
    """Persistent store; application predicates complement (not replace) PostgreSQL RLS."""

    def __init__(self, *, connection_factory: Callable[[], Any] | None = None, dsn: str | None = None) -> None:
        self._dsn = dsn or os.getenv("JANAVANI_CITIZEN_DOCUMENT_FORMAT_DSN")
        self._connection_factory = connection_factory
        if self._connection_factory is None and not self._dsn:
            raise ValueError("Dedicated citizen-format PostgreSQL DSN is required")

    def _connect(self) -> Any:
        if self._connection_factory:
            return self._connection_factory()
        import psycopg
        return psycopg.connect(self._dsn)

    @staticmethod
    def _hydrate(row: Any) -> CitizenDocumentFormat:
        return CitizenDocumentFormat(
            format_id=row[0], owner_principal_id=row[1], template_id=row[2],
            template_version=int(row[3]), section_field_names=tuple(row[4]),
            structure_hash=row[5], created_at=row[6].isoformat(), updated_at=row[7].isoformat(),
        )

    def save(self, record: CitizenDocumentFormat, *, owner_principal_id: str) -> CitizenDocumentFormat:
        if record.owner_principal_id != owner_principal_id:
            raise PermissionError("Format owner does not match authenticated principal")
        with self._connect() as conn:
            with conn.transaction():
                bind_postgres_principal(conn, owner_principal_id)
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO public.citizen_document_formats
                        (format_id, owner_principal_id, template_id, template_version,
                         section_field_names, structure_hash, created_at, updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (owner_principal_id, structure_hash)
                        DO UPDATE SET updated_at = citizen_document_formats.updated_at
                        RETURNING format_id, owner_principal_id, template_id, template_version,
                                  section_field_names, structure_hash, created_at, updated_at""",
                        (record.format_id, owner_principal_id, record.template_id,
                         record.template_version, list(record.section_field_names),
                         record.structure_hash, datetime.fromisoformat(record.created_at), datetime.fromisoformat(record.updated_at)),
                    )
                    return self._hydrate(cur.fetchone())

    def list_for_owner(self, *, owner_principal_id: str) -> list[CitizenDocumentFormat]:
        with self._connect() as conn:
            with conn.transaction():
                bind_postgres_principal(conn, owner_principal_id)
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT format_id, owner_principal_id, template_id, template_version,
                                  section_field_names, structure_hash, created_at, updated_at
                           FROM public.citizen_document_formats WHERE owner_principal_id = %s
                           ORDER BY created_at, format_id""",
                        (owner_principal_id,),
                    )
                    return [self._hydrate(row) for row in cur.fetchall()]

    def get_for_owner(self, format_id: str, *, owner_principal_id: str) -> CitizenDocumentFormat | None:
        with self._connect() as conn:
            with conn.transaction():
                bind_postgres_principal(conn, owner_principal_id)
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT format_id, owner_principal_id, template_id, template_version,
                                  section_field_names, structure_hash, created_at, updated_at
                           FROM public.citizen_document_formats
                           WHERE format_id = %s AND owner_principal_id = %s""",
                        (format_id, owner_principal_id),
                    )
                    row = cur.fetchone()
                    return self._hydrate(row) if row else None

    def delete_for_owner(self, format_id: str, *, owner_principal_id: str) -> bool:
        with self._connect() as conn:
            with conn.transaction():
                bind_postgres_principal(conn, owner_principal_id)
                with conn.cursor() as cur:
                    cur.execute(
                        """DELETE FROM public.citizen_document_formats
                           WHERE format_id = %s AND owner_principal_id = %s""",
                        (format_id, owner_principal_id),
                    )
                    return cur.rowcount == 1
