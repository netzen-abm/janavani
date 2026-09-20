import pytest

from src.core.civic_case import CivicCase, CaseType
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


def test_repository_contract_accepts_explicit_principal_context():
    repository = InMemoryCivicCaseRepository()
    case = CivicCase(
        case_id="principal-context-contract",
        case_type=CaseType.COMPLAINT,
        subject="Contract test",
        narrative="Explicit principal context",
        created_by="alice",
    )
    repository.save(case, principal_id="alice")
    assert repository.get(case.case_id, principal_id="alice") is case
