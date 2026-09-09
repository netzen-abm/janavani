import pytest

from src.storage.repositories.consent_provider import (
    ConsentProviderConfigurationError,
    create_consent_repository,
)


def test_consent_provider_defaults_to_memory():
    repository = create_consent_repository()
    assert repository.__class__.__name__ == "InMemoryConsentRepository"


def test_consent_provider_rejects_unknown_provider():
    with pytest.raises(ConsentProviderConfigurationError):
        create_consent_repository("unknown")


def test_postgres_consent_provider_requires_configuration():
    with pytest.raises(ConsentProviderConfigurationError):
        create_consent_repository("postgres")
