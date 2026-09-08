"""Shared application composition for provider-neutral Janavani capabilities."""
from __future__ import annotations

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.core.authority import AuthorityRepository
from src.core.evidence import EvidenceRepository
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.provider import create_civic_case_repository


def create_case_repository() -> CivicCaseRepository:
    """Compose the configured Case repository once for an application process."""
    return create_civic_case_repository()


def create_case_capability(repository: CivicCaseRepository) -> CivicCaseCapability:
    """Compose the shared Civic Case capability over an injected repository."""
    return CivicCaseCapability(repository)


def create_civic_action_capability(*, case_repository: CivicCaseRepository,
                                   authority_repository: AuthorityRepository,
                                   evidence_repository: EvidenceRepository | None = None,
                                   blob_store: ArtifactBlobStore | None = None) -> CivicActionCapability:
    """Compose the canonical Case → Evidence → Authority → Document boundary."""
    return CivicActionCapability(
        case_capability=create_case_capability(case_repository),
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        blob_store=blob_store,
    )


def create_authority_repository() -> AuthorityRepository:
    """Compose the configured authority provider; CSV remains an adapter."""
    return CsvAuthorityRepository()


def create_development_authority_repository() -> AuthorityRepository:
    """Provide a process-local authority provider for tests."""
    return InMemoryAuthorityRepository()


def create_development_evidence_repository() -> EvidenceRepository:
    """Provide a process-local evidence provider for tests."""
    return InMemoryEvidenceRepository()
