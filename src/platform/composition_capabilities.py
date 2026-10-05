"""Shared capability composition factories."""
from __future__ import annotations

import os

from src.capabilities.authority import AuthorityCapability
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.letter_drafting import LetterDraftingCapability
from src.capabilities.civic_action_vertical_slice import CivicActionVerticalSlice, CivicActionVerticalSliceDependencies
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.constitutional_objection import ConstitutionalObjectionCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.escalation import EscalationCapability
from src.capabilities.external_channel import ExternalChannelCapability
from src.capabilities.follow_up import FollowUpCapability
from src.capabilities.obligation import ObligationCapability
from src.capabilities.responsibility import ResponsibilityCapability
from src.capabilities.submission import SubmissionCapability, SubmissionTransport
from src.core.authority import AuthorityRepository
from src.core.evidence import EvidenceRepository
from src.core.obligation import ObligationResolver
from src.core.responsibility import ResponsibilityResolver
from src.core.submission import SubmissionRepository
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.document_review import DocumentReviewRepository
from src.storage.repositories.obligation import AuthorityBackedObligationResolver
from src.storage.repositories.responsibility import AuthorityBackedResponsibilityResolver
from src.storage.repositories.submission_case_transaction import SubmissionCaseTransactionRepository
from .composition_repositories import (create_document_review_repository_for_platform, create_external_channel_repository_for_platform, create_provider_composition, create_submission_repository)


def create_case_capability(repository: CivicCaseRepository) -> CivicCaseCapability:
    return CivicCaseCapability(repository)


def create_consent_capability(*, consent_repository: ConsentRepository, case_capability: CivicCaseCapability) -> ConsentCapability:
    return ConsentCapability(repository=consent_repository, case_capability=case_capability)


def create_authority_capability(repository: AuthorityRepository) -> AuthorityCapability:
    return AuthorityCapability(repository)


def create_responsibility_capability(resolver: ResponsibilityResolver) -> ResponsibilityCapability:
    return ResponsibilityCapability(resolver)


def create_obligation_capability(resolver: ObligationResolver) -> ObligationCapability:
    return ObligationCapability(resolver)


def create_external_channel_capability(*, provider_composition: ProviderComposition | None = None) -> ExternalChannelCapability:
    return ExternalChannelCapability(create_external_channel_repository_for_platform(provider_composition=provider_composition))


def create_follow_up_capability() -> FollowUpCapability:
    return FollowUpCapability()


def create_escalation_capability() -> EscalationCapability:
    return EscalationCapability()


def create_letter_drafting_capability(civic_action_capability: CivicActionCapability, document_review_capability) -> LetterDraftingCapability:
    return LetterDraftingCapability(civic_action_capability, document_review_capability)


def create_civic_action_capability(
    *,
    case_repository: CivicCaseRepository,
    authority_repository: AuthorityRepository,
    evidence_repository: EvidenceRepository | None = None,
    case_capability: CivicCaseCapability | None = None,
    document_review_capability: DocumentReviewCapability | None = None,
) -> CivicActionCapability:
    canonical_case_capability = case_capability or create_case_capability(case_repository)
    return CivicActionCapability(
        case_capability=canonical_case_capability,
        case_repository=case_repository,
        authority_capability=create_authority_capability(authority_repository),
        evidence_repository=evidence_repository,
        document_review_capability=document_review_capability,
    )



from .composition_vertical_slice import create_civic_action_vertical_slice

def create_constitutional_objection_capability(
    *,
    case_repository: CivicCaseRepository,
    authority_repository: AuthorityRepository,
    bill_profile_loader,
    evidence_repository: EvidenceRepository | None = None,
    document_review_capability: DocumentReviewCapability | None = None,
) -> ConstitutionalObjectionCapability:
    return ConstitutionalObjectionCapability(
        case_capability=create_case_capability(case_repository),
        case_repository=case_repository,
        authority_repository=authority_repository,
        bill_profile_loader=bill_profile_loader,
        evidence_repository=evidence_repository,
        document_review_capability=document_review_capability,
    )
