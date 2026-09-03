import pytest

from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.provider import (
    CivicCaseProviderConfigurationError,
    create_civic_case_repository,
)


def test_default_provider_is_memory():
    repository = create_civic_case_repository()
    assert isinstance(repository, InMemoryCivicCaseRepository)


def test_invalid_provider_is_rejected():
    with pytest.raises(CivicCaseProviderConfigurationError):
        create_civic_case_repository("unknown")


def test_postgres_provider_can_be_selected_with_injected_connection():
    repository = create_civic_case_repository(
        "postgres",
        connection_factory=lambda: None,
    )
    assert repository.__class__.__name__ == "PostgresCivicCaseRepository"


def test_supabase_provider_requires_a_client():
    with pytest.raises(CivicCaseProviderConfigurationError):
        create_civic_case_repository("supabase")
