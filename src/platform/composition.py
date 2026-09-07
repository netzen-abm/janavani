"""Shared application composition for provider-neutral Janavani capabilities."""
from __future__ import annotations

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.core.authority import AuthorityRepository
from src.core.evidence import EvidenceRepository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.provider import create_civic_case_repository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.authority import InMemoryAuthorityRepository


def create_case_repository() -> CivicCaseRepository:
    """Compose the configured Case repository once for an application process."""
    return create_civic_case_repository()


def create_case_capability(repository: CivicCaseRepository) -> CivicCaseCapability:
    """Compose the shared Civic Case capability over an injected repository."""
    return CivicCaseCapability(repository)


def create_civic_action_capability(
    *,
    case_repository: CivicCaseRepository,
    authority_repository: AuthorityRepository,
    evidence_repository: EvidenceRepository | None = None,
) -> CivicActionCapability:
    """Compose the canonical Case → Evidence → Authority → Document boundary."""
    return CivicActionCapability(
        case_capability=create_case_capability(case_repository),
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
    )


def create_development_authority_repository() -> AuthorityRepository:
    """Provide a process-local authority provider for development/tests."""
    return InMemoryAuthorityRepository()


def create_development_evidence_repository() -> EvidenceRepository:
    """Provide a process-local evidence provider for development/tests."""
    return InMemoryEvidenceRepository()
