"""Shared provider selection for citizen-owned document format persistence."""
from __future__ import annotations

import os

from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.citizen_document_format import (
    CitizenDocumentFormatRepository,
    InMemoryCitizenDocumentFormatRepository,
)
from src.storage.repositories.postgres_citizen_document_format import PostgresCitizenDocumentFormatRepository

SUPPORTED_CITIZEN_FORMAT_PROVIDERS = frozenset({"memory", "postgres"})


class CitizenDocumentFormatProviderConfigurationError(RuntimeError):
    """Raised when saved formats would otherwise use unsafe ephemeral persistence."""


def create_citizen_document_format_repository(
    *, composition: ProviderComposition | None = None,
    connection_factory=None, dsn: str | None = None,
) -> CitizenDocumentFormatRepository:
    selected = (
        (composition or ProviderComposition.from_environment()).provider_for("citizen_document_format")
    ).strip().lower()
    if selected not in SUPPORTED_CITIZEN_FORMAT_PROVIDERS:
        raise CitizenDocumentFormatProviderConfigurationError("Unsupported saved-format persistence provider")
    if selected == "memory":
        mode = os.getenv("JANAVANI_RUNTIME_MODE", "production").strip().lower()
        explicitly_enabled = os.getenv("JANAVANI_CITIZEN_DOCUMENT_FORMAT_ALLOW_EPHEMERAL", "").lower() == "true"
        if mode != "test" and not (mode != "production" and explicitly_enabled):
            raise CitizenDocumentFormatProviderConfigurationError(
                "Saved formats require durable storage; ephemeral persistence is disabled"
            )
        return InMemoryCitizenDocumentFormatRepository()
    try:
        return PostgresCitizenDocumentFormatRepository(
            connection_factory=connection_factory,
            dsn=dsn or os.getenv("JANAVANI_CITIZEN_DOCUMENT_FORMAT_DSN"),
        )
    except (ValueError, TypeError) as exc:
        raise CitizenDocumentFormatProviderConfigurationError(
            "A dedicated saved-format PostgreSQL DSN is required"
        ) from exc
