"""Provider selection for the canonical CivicCase repository.

Selection is explicit and provider-neutral. Access surfaces request a
repository without importing a concrete database provider themselves.
"""
from __future__ import annotations

import os
from typing import Any

from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.civic_case import CivicCaseRepository, InMemoryCivicCaseRepository

SUPPORTED_PROVIDERS = frozenset({"memory", "postgres"})


class CivicCaseProviderConfigurationError(RuntimeError):
    """Raised when the configured Civic Case provider is invalid."""


def create_civic_case_repository(
    provider: str | None = None,
    *,
    composition: ProviderComposition | None = None,
    connection_factory: Any = None,
    dsn: str | None = None,
) -> CivicCaseRepository:
    """Build the configured Civic Case repository.

    The default is memory. PostgreSQL must be selected explicitly.
    """
    selected = (
        composition.provider_for("civic_case")
        if composition is not None
        else provider or os.getenv("JANAVANI_CASE_REPOSITORY_PROVIDER", "memory")
    ).strip().lower()

    if selected not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise CivicCaseProviderConfigurationError(
            f"Unsupported Civic Case provider '{selected}'. Expected one of: {supported}"
        )

    if selected == "memory":
        return InMemoryCivicCaseRepository()

    from src.storage.repositories.postgres_civic_case import PostgresCivicCaseRepository

    try:
        return PostgresCivicCaseRepository(connection_factory=connection_factory, dsn=dsn)
    except (ValueError, TypeError) as exc:
        raise CivicCaseProviderConfigurationError(
            "PostgreSQL provider requires a DSN or connection factory"
        ) from exc
