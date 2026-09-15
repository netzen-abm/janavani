"""Shared application composition for provider-neutral Janavani capabilities."""
from __future__ import annotations

from src.capabilities.authority import AuthorityCapability
from src.capabilities.civic_action_capability import CivicActionCapability
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
from src.storage.repositories.accountability_feedback_provider import (
    create_accountability_feedback_repository as create_feedback_repository,
)
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.document_review import DocumentReviewRepository, InMemoryDocumentReviewRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.external_channel import InMemoryExternalChannelRepository
from src.storage.repositories.provider import create_civic_case_repository
from src.storage.repositories.obligation import AuthorityBackedObligationResolver
from src.storage.repositories.responsibility import AuthorityBackedResponsibilityResolver
from src.storage.repositories.submission_provider import create_submission_repository


def create_provider_composition() -> ProviderComposition:
    """Create the shared provider plan used by access-surface composition."""
    return ProviderComposition.from_environment()


def create_case_repository(*, provider_composition: ProviderComposition | None = None) -> CivicCaseRepository:
    composition = provider_composition or create_provider_composition()
    return create_civic_case_repository(composition=composition)


def create_accountability_feedback_repository(
    *, provider_composition: ProviderComposition | None = None,
    path=None,
):
    """Create feedback persistence from the shared provider plan."""
    composition = provider_composition or create_provider_composition()
    return create_feedback_repository(composition=composition, path=path)


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


def create_external_channel_capability() -> ExternalChannelCapability:
    """Create the provider-neutral channel capability with an in-memory adapter."""
    return ExternalChannelCapability(InMemoryExternalChannelRepository())


def create_follow_up_capability() -> FollowUpCapability:
    """Create the provider- and surface-neutral follow-up decision capability."""
    return FollowUpCapability()


def create_escalation_capability() -> EscalationCapability:
    """Create the provider- and surface-neutral escalation decision capability."""
    return EscalationCapability()


def create_civic_action_capability(*, case_repository: CivicCaseRepository, authority_repository: AuthorityRepository,
                                    evidence_repository: EvidenceRepository | None = None) -> CivicActionCapability:
    case_capability = create_case_capability(case_repository)
    return CivicActionCapability(case_capability=case_capability, case_repository=case_repository,
                                 authority_capability=create_authority_capability(authority_repository),
                                 evidence_repository=evidence_repository)


def create_civic_action_vertical_slice(*, case_repository: CivicCaseRepository, authority_repository: AuthorityRepository,
                                       consent_repository: ConsentRepository, submission_transport: SubmissionTransport,
                                       submission_repository: SubmissionRepository | None = None,
                                       evidence_repository: EvidenceRepository | None = None,
                                       document_review_repository: DocumentReviewRepository | None = None,
                                       artifact_repository=None, blob_store=None,
                                       responsibility_resolver: ResponsibilityResolver | None = None,
                                       obligation_resolver: ObligationResolver | None = None,
                                       obligation_records: dict[str, list[dict[str, object]]] | None = None,
                                       external_channel_capability: ExternalChannelCapability | None = None,
                                       follow_up_capability: FollowUpCapability | None = None,
                                       escalation_capability: EscalationCapability | None = None) -> CivicActionVerticalSlice:
    """Compose one canonical civic-action slice with shared capability instances."""
    case_capability = create_case_capability(case_repository)
    authority_capability = create_authority_capability(authority_repository)
    evidence_capability = EvidenceCapability(evidence_repository, case_capability) if evidence_repository is not None else None
    civic_action_capability = CivicActionCapability(case_capability=case_capability, case_repository=case_repository,
                                                    authority_capability=authority_capability,
                                                    evidence_repository=evidence_repository)
    review_repository = document_review_repository or InMemoryDocumentReviewRepository()
    document_review_capability = DocumentReviewCapability(review_repository, case_capability=case_capability)
    submission_repo = submission_repository or create_submission_repository()
    submission_capability = SubmissionCapability(case_capability, consent_repository, submission_transport,
                                                 submission_repository=submission_repo)
    resolver = responsibility_resolver or AuthorityBackedResponsibilityResolver(authority_repository)
    obligation = obligation_resolver or AuthorityBackedObligationResolver(obligation_records or {})
    obligation_capability = create_obligation_capability(obligation)
    channel_capability = external_channel_capability or create_external_channel_capability()
    follow_up = follow_up_capability or create_follow_up_capability()
    escalation = escalation_capability or create_escalation_capability()
    if evidence_capability is None:
        raise ValueError("An evidence repository is required for the canonical civic-action slice")
    return CivicActionVerticalSlice(CivicActionVerticalSliceDependencies(
        case_capability=case_capability, civic_action_capability=civic_action_capability,
        evidence_capability=evidence_capability, document_review_capability=document_review_capability,
        submission_capability=submission_capability, responsibility_capability=create_responsibility_capability(resolver),
        obligation_capability=obligation_capability, external_channel_capability=channel_capability,
        case_repository=case_repository, document_review_repository=review_repository,
        artifact_repository=artifact_repository, blob_store=blob_store, follow_up_capability=follow_up,
        escalation_capability=escalation))


def create_constitutional_objection_capability(*, case_repository: CivicCaseRepository, authority_repository: AuthorityRepository,
                                               bill_profile_loader, evidence_repository: EvidenceRepository | None = None) -> ConstitutionalObjectionCapability:
    return ConstitutionalObjectionCapability(case_capability=create_case_capability(case_repository), case_repository=case_repository,
                                             authority_repository=authority_repository, bill_profile_loader=bill_profile_loader,
                                             evidence_repository=evidence_repository)


def create_authority_repository() -> AuthorityRepository:
    return CsvAuthorityRepository()


def create_development_authority_repository() -> AuthorityRepository:
    return InMemoryAuthorityRepository()


def create_development_evidence_repository() -> EvidenceRepository:
    return InMemoryEvidenceRepository()
