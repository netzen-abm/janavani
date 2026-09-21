"""Canonical end-to-end civic-action orchestration boundary.

This module composes existing provider- and surface-neutral capabilities. It does
not own Case, Evidence, Authority, Document, Consent, Submission, Responsibility,
Obligation, External Channel, Follow-up, or Escalation semantics. Access surfaces should use this
orchestration boundary rather than rebuilding the civic-action lifecycle themselves.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.capabilities.document_review import DocumentReviewCapability, DocumentReviewRequest
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.escalation import EscalationCapability, EscalationContext, EscalationRecommendation
from src.capabilities.external_channel import ExternalChannelCapability, ExternalChannelQuery
from src.capabilities.follow_up import FollowUpCapability, FollowUpContext, FollowUpRecommendation
from src.capabilities.obligation import ObligationCapability, ObligationResolutionRequest
from src.capabilities.responsibility import ResponsibilityCapability, ResponsibilityResolutionRequest
from src.capabilities.submission import SubmissionCapability, SubmissionRequest
from src.core.delivery_channel import ExternalChannel
from src.core.obligation import ObligationResolution
from src.core.responsibility import ResponsibilityResolution
from src.documents.document_contract import DocumentDraft
from src.capabilities.civic_action_vertical_slice_document import CivicActionDocuments
from src.identity.context import IdentityContext
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.artifact_provider import create_document_artifact_repository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.document_artifact import DocumentArtifactRepository
from src.storage.repositories.document_review import DocumentReviewRepository


@dataclass(frozen=True)
class CivicActionVerticalSliceDependencies:
    """All capabilities required by the canonical civic-action slice."""

    case_capability: CivicCaseCapability
    civic_action_capability: CivicActionCapability
    evidence_capability: EvidenceCapability
    document_review_capability: DocumentReviewCapability
    submission_capability: SubmissionCapability
    responsibility_capability: ResponsibilityCapability
    obligation_capability: ObligationCapability
    external_channel_capability: ExternalChannelCapability
    case_repository: CivicCaseRepository
    document_review_repository: DocumentReviewRepository
    artifact_repository: DocumentArtifactRepository | None = None
    blob_store: ArtifactBlobStore | None = None
    follow_up_capability: FollowUpCapability | None = None
    escalation_capability: EscalationCapability | None = None


@dataclass(frozen=True)
class PreparedDocument:
    """A canonical draft persisted for user review before artifact generation."""

    case_id: str
    document_id: str
    draft: DocumentDraft


class CivicActionVerticalSlice:
    """Compose one complete civic-action path without duplicating domain logic."""

    def __init__(self, dependencies: CivicActionVerticalSliceDependencies) -> None:
        self._deps = dependencies
        self._documents = CivicActionDocuments(dependencies)

    def resolve_responsibility(
        self,
        request: ResponsibilityResolutionRequest,
    ) -> ResponsibilityResolution:
        """Resolve traceable responsibility candidates without asserting liability."""
        return self._deps.responsibility_capability.resolve(request)

    def resolve_obligation(
        self,
        request: ObligationResolutionRequest,
    ) -> ObligationResolution:
        """Resolve source-backed obligations for an already identified authority."""
        return self._deps.obligation_capability.resolve(request)

    def discover_external_channels(
        self,
        query: ExternalChannelQuery | None = None,
    ) -> tuple[ExternalChannel, ...]:
        """Expose only source-backed, currently verified external destinations."""
        return self._deps.external_channel_capability.discover(query)

    def get_verified_external_channel(self, channel_id: str) -> ExternalChannel:
        """Select one verified external destination through the shared channel boundary."""
        return self._deps.external_channel_capability.get_verified(channel_id)

    def recommend_follow_up(
        self,
        context: FollowUpContext,
    ) -> FollowUpRecommendation:
        """Recommend a user-controlled next step from canonical Case state and history."""
        capability = self._deps.follow_up_capability or FollowUpCapability()
        return capability.recommend(context)

    def recommend_escalation(
        self,
        context: EscalationContext,
    ) -> EscalationRecommendation:
        """Recommend a user-controlled escalation step from canonical Case state and history."""
        capability = self._deps.escalation_capability or EscalationCapability()
        return capability.recommend(context)

    def attach_evidence(self, case_id: str, evidence_id: str, *, identity: IdentityContext,
                        source_channel: str | None = None) -> CivicCaseResult:
        """Attach evidence only through the canonical Evidence capability boundary."""
        return self._deps.evidence_capability.attach(
            case_id,
            evidence_id,
            identity=identity,
            source_channel=source_channel or "shared",
        )

    def add_consent(self, case_id: str, consent_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        """Attach a previously recorded consent through the canonical Case boundary."""
        return self._deps.case_capability.add_consent(case_id, consent_id, identity=identity)

    def prepare_document(self, case_id: str, *, identity: IdentityContext, document_id=None):
        draft = self._documents.prepare(case_id, identity=identity, document_id=document_id)
        return PreparedDocument(case_id=case_id, document_id=draft.document_id, draft=draft)

    def review_document(self, request: DocumentReviewRequest, *, identity: IdentityContext):
        return self._documents.review(request, identity=identity)

    def start_review(self, case_id: str, *, identity: IdentityContext):
        return self._documents.start_review(case_id, identity=identity)

    def approve(self, case_id: str, *, identity: IdentityContext):
        return self._documents.approve(case_id, identity=identity)

    def generate_artifact(self, document_id: str, *, identity: IdentityContext, case_id=None,
                          document_format=None, output_dir=None):
        kwargs = {"identity": identity, "case_id": case_id}
        if document_format is not None: kwargs["document_format"] = document_format
        if output_dir is not None: kwargs["output_dir"] = output_dir
        return self._documents.generate(document_id, **kwargs)

    def submit(self, request: SubmissionRequest, *, channel_id: str, identity: IdentityContext,
               explicit_user_approval: bool) -> CivicCaseResult:
        """Submit only after resolving a currently verified External Channel.

        The channel registry remains control-plane metadata; SubmissionCapability
        remains responsible for authorization, consent, approval, idempotency,
        delivery and reconciliation. The caller cannot supply an arbitrary
        destination through this canonical orchestration boundary.
        """
        channel = self._deps.external_channel_capability.get_verified(channel_id)
        if request.destination_ref and request.destination_ref != channel.destination_ref:
            raise ValueError("Submission destination does not match the verified external channel")
        verified_request = request.__class__(
            case_id=request.case_id,
            document_id=request.document_id,
            destination_ref=channel.destination_ref,
            consent_scope=request.consent_scope,
            source_channel=request.source_channel,
            artifact_id=request.artifact_id,
            idempotency_key=request.idempotency_key,
        )
        return self._deps.submission_capability.submit(
            verified_request, identity=identity, explicit_user_approval=explicit_user_approval
        )
