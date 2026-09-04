"""Portable PostgreSQL provider for document artifact metadata."""
from __future__ import annotations

import os
from typing import Any, Callable

from src.documents.artifact_ref import ArtifactState, DocumentArtifactRef


class PostgresDocumentArtifactRepository:
    """PostgreSQL artifact metadata provider with no vendor-specific APIs."""

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
                    CREATE TABLE IF NOT EXISTS document_artifacts (
                        artifact_id TEXT PRIMARY KEY,
                        document_id TEXT NOT NULL,
                        case_id TEXT NOT NULL,
                        format TEXT NOT NULL,
                        storage_ref TEXT NOT NULL,
                        content_sha256 TEXT,
                        state TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS document_artifacts_case_idx "
                    "ON document_artifacts(case_id)"
                )

    def save(self, artifact: DocumentArtifactRef) -> None:
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO document_artifacts (
                            artifact_id, document_id, case_id, format,
                            storage_ref, content_sha256, state
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (artifact_id) DO UPDATE SET
                            document_id=EXCLUDED.document_id,
                            case_id=EXCLUDED.case_id,
                            format=EXCLUDED.format,
                            storage_ref=EXCLUDED.storage_ref,
                            content_sha256=EXCLUDED.content_sha256,
                            state=EXCLUDED.state
                        """,
                        (
                            artifact.artifact_id,
                            artifact.document_id,
                            artifact.case_id,
                            artifact.format,
                            artifact.storage_ref,
                            artifact.content_sha256,
                            artifact.state.value,
                        ),
                    )

    def get(self, artifact_id: str) -> DocumentArtifactRef | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT artifact_id, document_id, case_id, format, "
                    "storage_ref, content_sha256, state "
                    "FROM document_artifacts WHERE artifact_id = %s",
                    (artifact_id,),
                )
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    def list_for_case(self, case_id: str) -> list[DocumentArtifactRef]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT artifact_id, document_id, case_id, format, "
                    "storage_ref, content_sha256, state "
                    "FROM document_artifacts WHERE case_id = %s "
                    "ORDER BY artifact_id",
                    (case_id,),
                )
                rows = cursor.fetchall()
        return [self._hydrate(row) for row in rows]

    @staticmethod
    def _hydrate(row: Any) -> DocumentArtifactRef:
        return DocumentArtifactRef(
            artifact_id=row[0],
            document_id=row[1],
            case_id=row[2],
            format=row[3],
            storage_ref=row[4],
            content_sha256=row[5],
            state=ArtifactState(row[6]),
        )
