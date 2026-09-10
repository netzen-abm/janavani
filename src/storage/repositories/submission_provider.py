"""Provider selection for submission delivery metadata."""
from __future__ import annotations

import os
from typing import Any

from src.core.submission import SubmissionRepository
from src.storage.repositories.submission import InMemorySubmissionRepository

SUPPORTED_SUBMISSION_PROVIDERS = frozenset({"memory", "postgres"})


class SubmissionProviderConfigurationError(RuntimeError):
    """Raised when submission persistence is misconfigured."""


def create_submission_repository(
    provider: str | None = None,
    *,
    connection_factory: Any = None,
    dsn: str | None = None,
) -> SubmissionRepository:
    selected = (
        provider or os.getenv("JANAVANI_SUBMISSION_REPOSITORY_PROVIDER", "memory")
    ).strip().lower()
    if selected not in SUPPORTED_SUBMISSION_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_SUBMISSION_PROVIDERS))
        raise SubmissionProviderConfigurationError(
            f"Unsupported submission provider '{selected}'. Expected: {supported}"
        )
    if selected == "memory":
        return InMemorySubmissionRepository()
    from src.storage.repositories.postgres_submission import PostgresSubmissionRepository
    try:
        return PostgresSubmissionRepository(
            connection_factory=connection_factory,
            dsn=dsn,
        )
    except (ValueError, TypeError) as exc:
        raise SubmissionProviderConfigurationError(
            "PostgreSQL submission provider requires a DSN or connection factory"
        ) from exc
