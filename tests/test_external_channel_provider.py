import pytest

from src.platform.composition import create_external_channel_capability
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.external_channel import InMemoryExternalChannelRepository
from src.storage.repositories.external_channel_provider import (
    ExternalChannelProviderConfigurationError,
    create_external_channel_repository,
)


def test_memory_provider_is_selected_by_shared_composition():
    composition = ProviderComposition.memory_first()
    repository = create_external_channel_repository(composition=composition)
    assert isinstance(repository, InMemoryExternalChannelRepository)


def test_platform_composition_uses_shared_external_channel_provider():
    composition = ProviderComposition.memory_first()
    capability = create_external_channel_capability(provider_composition=composition)
    assert capability is not None


def test_unsupported_durable_provider_fails_closed():
    composition = ProviderComposition.memory_first().with_provider(
        "external_channel", "postgres"
    )
    with pytest.raises(ExternalChannelProviderConfigurationError):
        create_external_channel_repository(composition=composition)
