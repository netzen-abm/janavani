"""Explicit provider selection for the canonical consent repository."""
from __future__ import annotations

import os
from typing import Any

from src.storage.repositories.consent import ConsentRepository, InMemoryConsentRepository

SUPPORTED_CONSENT_PROVIDERS = frozenset({"memory", "postgres"})


class ConsentProviderConfigurationError(RuntimeError):
    """Raised when the configured consent provider is invalid."""


def create_consent_repository(
    provider: str | None = None,
    *,
    connection_factory: Any = None,
    dsn: str | None = None,
) -> ConsentRepository:
    """Build the configured consent repository without exposing provider details to surfaces."""
    selected = (provider or os.getenv("JANAVANI_CONSENT_REPOSITORY_PROVIDER", "memory")).strip().lower()
    if selected not in SUPPORTED_CONSENT_PROVIDERS:
        raise ConsentProviderConfigurationError(
            f"Unsupported consent provider '{selected}'. Expected one of: {', '.join(sorted(SUPPORTED_CONSENT_PROVIDERS))}"
        )
    if selected == "memory":
        return InMemoryConsentRepository()
    try:
        from src.storage.repositories.postgres_consent import PostgresConsentRepository
        return PostgresConsentRepository(connection_factory=connection_factory, dsn=dsn)
    except (ValueError, TypeError) as exc:
        raise ConsentProviderConfigurationError(
            "PostgreSQL consent provider requires a DSN or connection factory"
        ) from exc
