"""Portable SQLite provider for evidence metadata."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.core.evidence import EvidenceObject, EvidenceSource, validate_sha256


class SqliteEvidenceRepository:
    """Durable evidence metadata repository for local/single-node use."""

    def __init__(self, path: str | Path = "database/evidence.sqlite3") -> None:
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
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    evidence_type TEXT NOT NULL,
                    storage_ref TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    captured_at TEXT,
                    source_description TEXT,
                    provenance_json TEXT NOT NULL,
                    access_policy_ref TEXT,
                    retention_policy_ref TEXT,
                    status TEXT NOT NULL
                )
                """
            )

    def get(self, evidence_id: str) -> EvidenceObject | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM evidence WHERE evidence_id = ?",
                (evidence_id,),
            ).fetchone()
        return self._hydrate(row) if row else None

    def save(self, evidence: EvidenceObject) -> None:
        import json

        digest = validate_sha256(evidence.sha256)
        provenance = json.dumps(
            [source.__dict__ for source in evidence.provenance],
            sort_keys=True,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO evidence (
                    evidence_id, evidence_type, storage_ref, sha256,
                    received_at, captured_at, source_description,
                    provenance_json, access_policy_ref,
                    retention_policy_ref, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    evidence_type=excluded.evidence_type,
                    storage_ref=excluded.storage_ref,
                    sha256=excluded.sha256,
                    received_at=excluded.received_at,
                    captured_at=excluded.captured_at,
                    source_description=excluded.source_description,
                    provenance_json=excluded.provenance_json,
                    access_policy_ref=excluded.access_policy_ref,
                    retention_policy_ref=excluded.retention_policy_ref,
                    status=excluded.status
                """,
                (
                    evidence.evidence_id,
                    evidence.evidence_type,
                    evidence.storage_ref,
                    digest,
                    evidence.received_at,
                    evidence.captured_at,
                    evidence.source_description,
                    provenance,
                    evidence.access_policy_ref,
                    evidence.retention_policy_ref,
                    evidence.status,
                ),
            )

    @staticmethod
    def _hydrate(row: sqlite3.Row) -> EvidenceObject:
        import json

        provenance = tuple(
            EvidenceSource(**item)
            for item in json.loads(row["provenance_json"])
        )
        return EvidenceObject(
            evidence_id=row["evidence_id"],
            evidence_type=row["evidence_type"],
            storage_ref=row["storage_ref"],
            sha256=row["sha256"],
            received_at=row["received_at"],
            captured_at=row["captured_at"],
            source_description=row["source_description"],
            provenance=provenance,
            access_policy_ref=row["access_policy_ref"],
            retention_policy_ref=row["retention_policy_ref"],
            status=row["status"],
        )
