"""Shared capability composition factories."""
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
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.document_review import DocumentReviewRepository
from src.storage.repositories.obligation import AuthorityBackedObligationResolver
from src.storage.repositories.responsibility import AuthorityBackedResponsibilityResolver
from .composition_repositories import create_document_review_repository_for_platform, create_provider_composition, create_submission_repository, create_external_channel_repository_for_platform

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

def create_civic_action_capability(*, case_repository: CivicCaseRepository, authority_repository: AuthorityRepository, evidence_repository: EvidenceRepository | None = None) -> CivicActionCapability:
    return CivicActionCapability(case_capability=create_case_capability(case_repository), case_repository=case_repository, authority_capability=create_authority_capability(authority_repository), evidence_repository=evidence_repository)

def create_civic_action_vertical_slice(*, case_repository: CivicCaseRepository, authority_repository: AuthorityRepository,
                                       consent_repository: ConsentRepository, submission_transport: SubmissionTransport,
                                       submission_repository: SubmissionRepository | None = None, evidence_repository: EvidenceRepository | None = None,
                                       document_review_repository: DocumentReviewRepository | None = None, artifact_repository=None, blob_store=None,
                                       responsibility_resolver: ResponsibilityResolver | None = None, obligation_resolver: ObligationResolver | None = None,
                                       obligation_records: dict[str, list[dict[str, object]]] | None = None,
                                       external_channel_capability: ExternalChannelCapability | None = None,
                                       follow_up_capability: FollowUpCapability | None = None, escalation_capability: EscalationCapability | None = None,
                                       provider_composition: ProviderComposition | None = None) -> CivicActionVerticalSlice:
    composition = provider_composition or create_provider_composition()
    case_capability = create_case_capability(case_repository)
    authority_capability = create_authority_capability(authority_repository)
    if evidence_repository is None:
        raise ValueError("An evidence repository is required for the canonical civic-action slice")
    evidence_capability = EvidenceCapability(evidence_repository, case_capability)
    civic_action_capability = CivicActionCapability(case_capability=case_capability, case_repository=case_repository, authority_capability=authority_capability, evidence_repository=evidence_repository)
    review_repository = document_review_repository or create_document_review_repository_for_platform(provider_composition=composition)
    document_review_capability = DocumentReviewCapability(review_repository, case_capability=case_capability)
    submission_repo = submission_repository or create_submission_repository(provider_composition=composition)
    submission_capability = SubmissionCapability(case_capability, consent_repository, submission_transport, submission_repository=submission_repo)
    resolver = responsibility_resolver or AuthorityBackedResponsibilityResolver(authority_repository)
    obligation = obligation_resolver or AuthorityBackedObligationResolver(obligation_records or {})
    return CivicActionVerticalSlice(CivicActionVerticalSliceDependencies(
        case_capability=case_capability, civic_action_capability=civic_action_capability, evidence_capability=evidence_capability,
        document_review_capability=document_review_capability, submission_capability=submission_capability,
        responsibility_capability=create_responsibility_capability(resolver), obligation_capability=create_obligation_capability(obligation),
        external_channel_capability=external_channel_capability or create_external_channel_capability(provider_composition=composition),
        case_repository=case_repository, document_review_repository=review_repository, artifact_repository=artifact_repository, blob_store=blob_store,
        follow_up_capability=follow_up_capability or create_follow_up_capability(), escalation_capability=escalation_capability or create_escalation_capability(),
    ))

def create_constitutional_objection_capability(*, case_repository: CivicCaseRepository, authority_repository: AuthorityRepository, bill_profile_loader, evidence_repository: EvidenceRepository | None = None) -> ConstitutionalObjectionCapability:
    return ConstitutionalObjectionCapability(case_capability=create_case_capability(case_repository), case_repository=case_repository, authority_repository=authority_repository, bill_profile_loader=bill_profile_loader, evidence_repository=evidence_repository)
