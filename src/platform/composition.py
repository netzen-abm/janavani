"""Shared application composition for provider-neutral Janavani capabilities."""
from __future__ import annotations

from src.capabilities.authority import AuthorityCapability
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.constitutional_objection import ConstitutionalObjectionCapability
from src.core.authority import AuthorityRepository
from src.core.evidence import EvidenceRepository
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.provider import create_civic_case_repository


def create_case_repository() -> CivicCaseRepository:
    return create_civic_case_repository()


def create_case_capability(repository: CivicCaseRepository) -> CivicCaseCapability:
    return CivicCaseCapability(repository)


def create_authority_capability(repository: AuthorityRepository) -> AuthorityCapability:
    return AuthorityCapability(repository)


def create_civic_action_capability(
    *,
    case_repository: CivicCaseRepository,
    authority_repository: AuthorityRepository,
    evidence_repository: EvidenceRepository | None = None,
) -> CivicActionCapability:
    return CivicActionCapability(
        case_capability=create_case_capability(case_repository),
        case_repository=case_repository,
        authority_capability=create_authority_capability(authority_repository),
        evidence_repository=evidence_repository,
    )


def create_constitutional_objection_capability(
    *,
    case_repository: CivicCaseRepository,
    authority_repository: AuthorityRepository,
    bill_profile_loader,
    evidence_repository: EvidenceRepository | None = None,
) -> ConstitutionalObjectionCapability:
    return ConstitutionalObjectionCapability(
        case_capability=create_case_capability(case_repository),
        case_repository=case_repository,
        authority_repository=authority_repository,
        bill_profile_loader=bill_profile_loader,
        evidence_repository=evidence_repository,
    )


def create_authority_repository() -> AuthorityRepository:
    return CsvAuthorityRepository()


def create_development_authority_repository() -> AuthorityRepository:
    return InMemoryAuthorityRepository()


def create_development_evidence_repository() -> EvidenceRepository:
    return InMemoryEvidenceRepository()
