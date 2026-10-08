from __future__ import annotations

from src.capabilities.civic_action_vertical_slice import CivicActionVerticalSlice, CivicActionVerticalSliceDependencies
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.submission import SubmissionCapability
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.authority import AuthorityCapability
from src.capabilities.responsibility import ResponsibilityCapability
from src.capabilities.obligation import ObligationCapability
from src.capabilities.external_channel import ExternalChannelCapability
from src.capabilities.follow_up import FollowUpCapability
from src.capabilities.escalation import EscalationCapability
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.obligation import AuthorityBackedObligationResolver
from src.storage.repositories.responsibility import AuthorityBackedResponsibilityResolver
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.document_review import DocumentReviewRepository
from src.storage.repositories.submission_case_transaction import SubmissionCaseTransactionRepository
from src.core.responsibility import ResponsibilityResolver
from src.core.authority import AuthorityRepository
from src.core.evidence import EvidenceRepository
from src.core.obligation import ObligationResolver
from .composition_repositories import create_document_review_repository_for_platform, create_provider_composition

def create_civic_action_vertical_slice(
    *,
    case_repository: CivicCaseRepository,
    authority_repository: AuthorityRepository,
    consent_repository: ConsentRepository,
    case_capability: CivicCaseCapability | None = None,
    evidence_repository: EvidenceRepository | None = None,
    document_review_repository: DocumentReviewRepository | None = None,
    artifact_repository=None,
    blob_store=None,
    responsibility_resolver: ResponsibilityResolver | None = None,
    obligation_resolver: ObligationResolver | None = None,
    obligation_records: dict[str, list[dict[str, object]]] | None = None,
    external_channel_capability: ExternalChannelCapability | None = None,
    follow_up_capability: FollowUpCapability | None = None,
    escalation_capability: EscalationCapability | None = None,
    submission_capability: SubmissionCapability | None = None,
    submission_transport=None,
    provider_composition: ProviderComposition | None = None,
) -> CivicActionVerticalSlice:
    from .composition_capabilities import (
        create_case_capability, create_authority_capability,
        create_responsibility_capability, create_obligation_capability,
        create_external_channel_capability, create_follow_up_capability,
        create_escalation_capability,
    )
    composition = provider_composition or create_provider_composition()
    case_capability = case_capability or create_case_capability(
        case_repository,
        content_repository=getattr(case_repository, "content_repository", None),
    )
    authority_capability = create_authority_capability(authority_repository)
    if evidence_repository is None:
        raise ValueError("An evidence repository is required for the canonical civic-action slice")
    evidence_capability = EvidenceCapability(evidence_repository, case_capability)
    civic_action_capability = CivicActionCapability(
        case_capability=case_capability,
        case_repository=case_repository,
        authority_capability=authority_capability,
        evidence_repository=evidence_repository,
    )
    review_repository = document_review_repository or create_document_review_repository_for_platform(provider_composition=composition)
    document_review_capability = DocumentReviewCapability(
        review_repository, case_capability=case_capability
    )
    resolver = responsibility_resolver or AuthorityBackedResponsibilityResolver(authority_repository)
    obligation = obligation_resolver or AuthorityBackedObligationResolver(obligation_records or {})
    if submission_capability is None and submission_transport is not None:
        submission_capability = SubmissionCapability(
            case_capability=case_capability,
            consent_repository=consent_repository,
            transport=submission_transport,
            evidence_repository=evidence_repository,
        )

    return CivicActionVerticalSlice(
        CivicActionVerticalSliceDependencies(
            case_capability=case_capability,
            civic_action_capability=civic_action_capability,
            evidence_capability=evidence_capability,
            document_review_capability=document_review_capability,
            responsibility_capability=create_responsibility_capability(resolver),
            obligation_capability=create_obligation_capability(obligation),
            submission_capability=submission_capability,
            external_channel_capability=external_channel_capability
            or create_external_channel_capability(provider_composition=composition),
            case_repository=case_repository,
            document_review_repository=review_repository,
            artifact_repository=artifact_repository,
            blob_store=blob_store,
            follow_up_capability=follow_up_capability or create_follow_up_capability(),
            escalation_capability=escalation_capability or create_escalation_capability(),
        )
    )

