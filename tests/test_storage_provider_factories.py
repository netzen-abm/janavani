"""Contract-level checks for provider selection boundaries."""
from __future__ import annotations

import pytest

from src.storage.repositories.artifact_provider import (
    DocumentArtifactProviderConfigurationError,
    create_document_artifact_repository,
)
from src.storage.repositories.document_artifact import (
    InMemoryDocumentArtifactRepository,
)
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.evidence_provider import (
    EvidenceProviderConfigurationError,
    create_evidence_repository,
)


def test_artifact_factory_defaults_to_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JANAVANI_ARTIFACT_REPOSITORY_PROVIDER", raising=False)
    assert isinstance(create_document_artifact_repository(), InMemoryDocumentArtifactRepository)


def test_evidence_factory_defaults_to_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JANAVANI_EVIDENCE_REPOSITORY_PROVIDER", raising=False)
    assert isinstance(create_evidence_repository(), InMemoryEvidenceRepository)


def test_artifact_factory_rejects_unknown_provider() -> None:
    with pytest.raises(DocumentArtifactProviderConfigurationError):
        create_document_artifact_repository("unknown")


def test_evidence_factory_rejects_unknown_provider() -> None:
    with pytest.raises(EvidenceProviderConfigurationError):
        create_evidence_repository("unknown")


def test_artifact_postgres_requires_configuration() -> None:
    with pytest.raises(DocumentArtifactProviderConfigurationError):
        create_document_artifact_repository("postgres")


def test_evidence_postgres_requires_configuration() -> None:
    with pytest.raises(EvidenceProviderConfigurationError):
        create_evidence_repository("postgres")
