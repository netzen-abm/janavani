import pytest

from src.storage.repositories.submission import InMemorySubmissionRepository
from src.storage.repositories.submission_provider import (
    SubmissionProviderConfigurationError,
    create_submission_repository,
)


def test_default_submission_repository_is_in_memory(monkeypatch):
    monkeypatch.delenv("JANAVANI_SUBMISSION_REPOSITORY_PROVIDER", raising=False)
    assert isinstance(create_submission_repository(), InMemorySubmissionRepository)


def test_unsupported_submission_provider_fails_closed():
    with pytest.raises(SubmissionProviderConfigurationError):
        create_submission_repository("unknown")


def test_postgres_submission_provider_requires_configuration():
    with pytest.raises(SubmissionProviderConfigurationError):
        create_submission_repository("postgres", dsn=None, connection_factory=None)
