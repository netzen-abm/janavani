"""Portable SQLite provider for document artifact metadata.

SQLite is a local durable provider, not a cloud dependency. The capability
contract remains independent of this implementation and can later be backed
by PostgreSQL or another provider without changing document-domain code.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.documents.artifact_ref import ArtifactState, DocumentArtifactRef


class SqliteDocumentArtifactRepository:
    """Durable artifact metadata repository for local/single-node use."""

    def __init__(self, path: str | Path = "database/artifacts.sqlite3") -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
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
            connection.execute(
                "CREATE INDEX IF NOT EXISTS document_artifacts_case_idx "
                "ON document_artifacts(case_id)"
            )

    def save(self, artifact: DocumentArtifactRef) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO document_artifacts (
                    artifact_id, document_id, case_id, format,
                    storage_ref, content_sha256, state
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(artifact_id) DO UPDATE SET
                    document_id=excluded.document_id,
                    case_id=excluded.case_id,
                    format=excluded.format,
                    storage_ref=excluded.storage_ref,
                    content_sha256=excluded.content_sha256,
                    state=excluded.state
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
            row = connection.execute(
                "SELECT * FROM document_artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
        return self._hydrate(row) if row else None

    def list_for_case(self, case_id: str) -> list[DocumentArtifactRef]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM document_artifacts "
                "WHERE case_id = ? ORDER BY artifact_id",
                (case_id,),
            ).fetchall()
        return [self._hydrate(row) for row in rows]

    @staticmethod
    def _hydrate(row: sqlite3.Row) -> DocumentArtifactRef:
        return DocumentArtifactRef(
            artifact_id=row["artifact_id"],
            document_id=row["document_id"],
            case_id=row["case_id"],
            format=row["format"],
            storage_ref=row["storage_ref"],
            content_sha256=row["content_sha256"],
            state=ArtifactState(row["state"]),
        )
