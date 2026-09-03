"""Provider selection for the canonical CivicCase repository.

Selection is explicit and provider-neutral. Access surfaces request a
repository without importing a concrete database provider themselves.
"""
from __future__ import annotations

import os
from typing import Any

from src.storage.repositories.civic_case import (
    CivicCaseRepository,
    InMemoryCivicCaseRepository,
)

SUPPORTED_PROVIDERS = frozenset({"memory", "postgres", "supabase"})


class CivicCaseProviderConfigurationError(RuntimeError):
    """Raised when the configured Civic Case provider is invalid."""


def create_civic_case_repository(
    provider: str | None = None,
    *,
    connection_factory: Any = None,
    dsn: str | None = None,
    supabase_client: Any = None,
) -> CivicCaseRepository:
    """Build the configured Civic Case repository.

    The default is ``memory`` so a deployment cannot silently acquire a
    durable external dependency. Durable providers must be selected
    explicitly with ``JANAVANI_CASE_REPOSITORY_PROVIDER`` or ``provider``.
    """
    selected = (
        provider
        or os.getenv("JANAVANI_CASE_REPOSITORY_PROVIDER", "memory")
    ).strip().lower()

    if selected not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise CivicCaseProviderConfigurationError(
            f"Unsupported Civic Case provider '{selected}'. "
            f"Expected one of: {supported}"
        )

    if selected == "memory":
        return InMemoryCivicCaseRepository()

    if selected == "postgres":
        from src.storage.repositories.postgres_civic_case import (
            PostgresCivicCaseRepository,
        )

        try:
            return PostgresCivicCaseRepository(
                connection_factory=connection_factory,
                dsn=dsn,
            )
        except (ValueError, TypeError) as exc:
            raise CivicCaseProviderConfigurationError(
                "PostgreSQL provider requires a DSN or connection factory"
            ) from exc

    if supabase_client is None:
        try:
            from src.storage.supabase import supabase
        except Exception as exc:
            raise CivicCaseProviderConfigurationError(
                "Supabase provider could not be initialized"
            ) from exc
        supabase_client = supabase

    if supabase_client is None:
        raise CivicCaseProviderConfigurationError(
            "Supabase provider requires a configured client"
        )

    from src.storage.repositories.supabase_civic_case import (
        SupabaseCivicCaseRepository,
    )

    try:
        return SupabaseCivicCaseRepository(supabase_client)
    except (ValueError, TypeError) as exc:
        raise CivicCaseProviderConfigurationError(
            "Supabase provider requires a configured client"
        ) from exc
