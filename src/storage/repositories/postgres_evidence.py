"""Portable PostgreSQL provider for evidence metadata."""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from src.core.evidence import EvidenceObject, EvidenceSource, validate_sha256


class PostgresEvidenceRepository:
    """PostgreSQL evidence metadata provider with no vendor-specific APIs."""

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
                    CREATE TABLE IF NOT EXISTS evidence_objects (
                        evidence_id TEXT PRIMARY KEY,
                        evidence_type TEXT NOT NULL,
                        storage_ref TEXT NOT NULL,
                        sha256 TEXT NOT NULL,
                        received_at TEXT NOT NULL,
                        captured_at TEXT,
                        source_description TEXT,
                        provenance JSONB NOT NULL DEFAULT '[]'::jsonb,
                        access_policy_ref TEXT,
                        retention_policy_ref TEXT,
                        status TEXT NOT NULL
                    )
                    """
                )

    def save(self, evidence: EvidenceObject) -> None:
        normalized = validate_sha256(evidence.sha256)
        provenance = [source.__dict__ for source in evidence.provenance]
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO evidence_objects (
                            evidence_id, evidence_type, storage_ref, sha256,
                            received_at, captured_at, source_description,
                            provenance, access_policy_ref, retention_policy_ref,
                            status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb,
                                  %s, %s, %s)
                        ON CONFLICT (evidence_id) DO UPDATE SET
                            evidence_type=EXCLUDED.evidence_type,
                            storage_ref=EXCLUDED.storage_ref,
                            sha256=EXCLUDED.sha256,
                            received_at=EXCLUDED.received_at,
                            captured_at=EXCLUDED.captured_at,
                            source_description=EXCLUDED.source_description,
                            provenance=EXCLUDED.provenance,
                            access_policy_ref=EXCLUDED.access_policy_ref,
                            retention_policy_ref=EXCLUDED.retention_policy_ref,
                            status=EXCLUDED.status
                        """,
                        (
                            evidence.evidence_id,
                            evidence.evidence_type,
                            evidence.storage_ref,
                            normalized,
                            evidence.received_at,
                            evidence.captured_at,
                            evidence.source_description,
                            json.dumps(provenance),
                            evidence.access_policy_ref,
                            evidence.retention_policy_ref,
                            evidence.status,
                        ),
                    )

    def get(self, evidence_id: str) -> EvidenceObject | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT evidence_id, evidence_type, storage_ref, sha256, "
                    "received_at, captured_at, source_description, provenance, "
                    "access_policy_ref, retention_policy_ref, status "
                    "FROM evidence_objects WHERE evidence_id = %s",
                    (evidence_id,),
                )
                row = cursor.fetchone()
        return self._hydrate(row) if row else None

    @staticmethod
    def _hydrate(row: Any) -> EvidenceObject:
        provenance = row[7]
        if isinstance(provenance, str):
            provenance = json.loads(provenance)
        sources = tuple(EvidenceSource(**source) for source in provenance or [])
        return EvidenceObject(
            evidence_id=row[0],
            evidence_type=row[1],
            storage_ref=row[2],
            sha256=validate_sha256(row[3]),
            received_at=row[4],
            captured_at=row[5],
            source_description=row[6],
            provenance=sources,
            access_policy_ref=row[8],
            retention_policy_ref=row[9],
            status=row[10],
        )
