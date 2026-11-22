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


def test_atomic_consent_provider_selects_transaction_for_shared_memory_repositories():
    from src.platform.composition_repositories import create_consent_case_atomic_repository
    from src.storage.provider_composition import ProviderComposition
    from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
    from src.storage.repositories.consent import InMemoryConsentRepository
    from src.storage.repositories.consent_case_atomic import InMemoryConsentCaseAtomicRepository

    providers = ProviderComposition.memory_first()
    consent_repository = InMemoryConsentRepository()
    case_repository = InMemoryCivicCaseRepository()
    atomic = create_consent_case_atomic_repository(
        provider_composition=providers,
        consent_repository=consent_repository,
        case_repository=case_repository,
    )

    assert isinstance(atomic, InMemoryConsentCaseAtomicRepository)
    assert atomic._consents is consent_repository
    assert atomic._cases is case_repository


def test_atomic_consent_provider_rejects_mixed_case_and_consent_providers():
    from src.platform.composition_repositories import create_consent_case_atomic_repository
    from src.storage.provider_composition import ProviderComposition
    from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
    from src.storage.repositories.consent import InMemoryConsentRepository

    providers = ProviderComposition.memory_first().with_provider("consent", "postgres")
    with pytest.raises(ValueError, match="same provider"):
        create_consent_case_atomic_repository(
            provider_composition=providers,
            consent_repository=InMemoryConsentRepository(),
            case_repository=InMemoryCivicCaseRepository(),
        )


def test_atomic_postgres_consent_requires_database_dsn(monkeypatch):
    from src.platform.composition_repositories import create_consent_case_atomic_repository
    from src.storage.provider_composition import ProviderComposition
    from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
    from src.storage.repositories.consent import InMemoryConsentRepository

    monkeypatch.delenv("JANAVANI_POSTGRES_DSN", raising=False)
    providers = (
        ProviderComposition.memory_first()
        .with_provider("consent", "postgres")
        .with_provider("civic_case", "postgres")
    )
    with pytest.raises(ValueError, match="JANAVANI_POSTGRES_DSN"):
        create_consent_case_atomic_repository(
            provider_composition=providers,
            consent_repository=InMemoryConsentRepository(),
            case_repository=InMemoryCivicCaseRepository(),
        )
