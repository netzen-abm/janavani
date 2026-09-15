"""Provider selection for the canonical external-channel registry.

The external-channel domain is persisted canonical data in the shared provider
plan, but only an in-memory adapter is currently implemented.  Durable
providers remain intentionally deferred until there is a verified channel
source, lifecycle, and persistence/migration contract.
"""
from __future__ import annotations

from src.core.delivery_channel import ExternalChannelRepository
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.external_channel import InMemoryExternalChannelRepository

SUPPORTED_PROVIDERS = frozenset({"memory"})


class ExternalChannelProviderConfigurationError(ValueError):
    """Raised when the requested external-channel provider is not implemented."""


def create_external_channel_repository(
    *,
    composition: ProviderComposition | None = None,
) -> ExternalChannelRepository:
    """Create the external-channel repository selected by shared composition.

    ``memory`` is the only supported implementation at present.  Unsupported
    durable providers fail closed rather than silently falling back to memory.
    """
    provider = (composition or ProviderComposition.memory_first()).provider_for(
        "external_channel"
    )
    if provider == "memory":
        return InMemoryExternalChannelRepository()
    raise ExternalChannelProviderConfigurationError(
        f"External channel provider '{provider}' is not implemented; "
        "configure 'memory' until a verified durable adapter exists"
    )
