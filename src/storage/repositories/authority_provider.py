"""Provider selection for the canonical Authority repository."""
from __future__ import annotations

import os
from typing import Any

from src.core.authority import AuthorityRepository
from src.storage.repositories.authority import InMemoryAuthorityRepository

SUPPORTED_PROVIDERS = frozenset({"memory", "postgres", "csv"})


class AuthorityProviderConfigurationError(RuntimeError):
    """Raised when the configured Authority provider is invalid."""


def create_authority_repository(
    provider: str | None = None,
    *,
    connection_factory: Any = None,
    dsn: str | None = None,
    csv_path: str | None = None,
) -> AuthorityRepository:
    """Build the configured authority repository without coupling callers to providers."""
    selected = (provider or os.getenv("JANAVANI_AUTHORITY_REPOSITORY_PROVIDER", "memory")).strip().lower()
    if selected not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise AuthorityProviderConfigurationError(
            f"Unsupported Authority provider '{selected}'. Expected one of: {supported}"
        )
    if selected == "memory":
        return InMemoryAuthorityRepository()
    if selected == "csv":
        from src.storage.repositories.authority_csv import CsvAuthorityRepository

        return CsvAuthorityRepository(csv_path)
    from src.storage.repositories.postgres_authority import PostgresAuthorityRepository

    try:
        return PostgresAuthorityRepository(connection_factory=connection_factory, dsn=dsn)
    except (ValueError, TypeError) as exc:
        raise AuthorityProviderConfigurationError(
            "PostgreSQL provider requires a DSN or connection factory"
        ) from exc
