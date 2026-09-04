"""Provider selection for document artifact metadata."""
from __future__ import annotations

import os
from typing import Any

from src.storage.repositories.document_artifact import (
    DocumentArtifactRepository,
    InMemoryDocumentArtifactRepository,
)

SUPPORTED_ARTIFACT_PROVIDERS = frozenset({"memory", "sqlite", "postgres"})


class DocumentArtifactProviderConfigurationError(RuntimeError):
    """Raised when artifact persistence is misconfigured."""


def create_document_artifact_repository(
    provider: str | None = None,
    *,
    path: str | None = None,
    connection_factory: Any = None,
    dsn: str | None = None,
) -> DocumentArtifactRepository:
    selected = (
        provider
        or os.getenv("JANAVANI_ARTIFACT_REPOSITORY_PROVIDER", "memory")
    ).strip().lower()
    if selected not in SUPPORTED_ARTIFACT_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_ARTIFACT_PROVIDERS))
        raise DocumentArtifactProviderConfigurationError(
            f"Unsupported artifact provider '{selected}'. Expected: {supported}"
        )
    if selected == "memory":
        return InMemoryDocumentArtifactRepository()
    if selected == "sqlite":
        from src.storage.repositories.sqlite_document_artifact import (
            SqliteDocumentArtifactRepository,
        )
        return SqliteDocumentArtifactRepository(path or "database/artifacts.sqlite3")
    from src.storage.repositories.postgres_document_artifact import (
        PostgresDocumentArtifactRepository,
    )
    try:
        return PostgresDocumentArtifactRepository(
            connection_factory=connection_factory,
            dsn=dsn,
        )
    except (ValueError, TypeError) as exc:
        raise DocumentArtifactProviderConfigurationError(
            "PostgreSQL artifact provider requires a DSN or connection factory"
        ) from exc
