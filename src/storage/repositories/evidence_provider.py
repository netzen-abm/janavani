"""Provider selection for evidence metadata."""
from __future__ import annotations

import os
from typing import Any

from src.core.evidence import EvidenceRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository

SUPPORTED_EVIDENCE_PROVIDERS = frozenset({"memory", "sqlite", "postgres"})


class EvidenceProviderConfigurationError(RuntimeError):
    """Raised when evidence persistence is misconfigured."""


def create_evidence_repository(
    provider: str | None = None,
    *,
    path: str | None = None,
    connection_factory: Any = None,
    dsn: str | None = None,
) -> EvidenceRepository:
    selected = (
        provider
        or os.getenv("JANAVANI_EVIDENCE_REPOSITORY_PROVIDER", "memory")
    ).strip().lower()
    if selected not in SUPPORTED_EVIDENCE_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_EVIDENCE_PROVIDERS))
        raise EvidenceProviderConfigurationError(
            f"Unsupported evidence provider '{selected}'. Expected: {supported}"
        )
    if selected == "memory":
        return InMemoryEvidenceRepository()
    if selected == "sqlite":
        from src.storage.repositories.sqlite_evidence import SqliteEvidenceRepository
        return SqliteEvidenceRepository(path or "database/evidence.sqlite3")
    from src.storage.repositories.postgres_evidence import PostgresEvidenceRepository
    try:
        return PostgresEvidenceRepository(
            connection_factory=connection_factory,
            dsn=dsn,
        )
    except (ValueError, TypeError) as exc:
        raise EvidenceProviderConfigurationError(
            "PostgreSQL evidence provider requires a DSN or connection factory"
        ) from exc
