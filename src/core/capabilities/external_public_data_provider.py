"""Registry for channel-neutral external public civic-data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.contracts.external_public_data import ExternalDataRecord


class ExternalPublicDataProvider(ABC):
    provider_id: str

    @abstractmethod
    def search(self, query: dict[str, Any]) -> tuple[ExternalDataRecord, ...]:
        """Return contextual records with provenance; never legal conclusions."""


class SharedExternalPublicDataRegistry:
    def __init__(self, providers: tuple[ExternalPublicDataProvider, ...] = ()):
        self._providers = {p.provider_id: p for p in providers}

    def register(self, provider: ExternalPublicDataProvider) -> None:
        if not provider.provider_id:
            raise ValueError("provider_id is required")
        self._providers[provider.provider_id] = provider

    def search(self, provider_id: str, query: dict[str, Any]) -> tuple[ExternalDataRecord, ...]:
        return self._providers[provider_id].search(query)
