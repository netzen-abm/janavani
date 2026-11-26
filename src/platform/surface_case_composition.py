"""Compose the shared Case capability graph for independent access surfaces."""
from __future__ import annotations

from dataclasses import dataclass

from src.capabilities.authority import AuthorityCapability
from src.identity.linking import ExternalIdentityLinkRepository
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.capabilities.letter_drafting import LetterDraftingCapability
from src.capabilities.submission_contract import SubmissionTransport
from src.platform.composition_capabilities import create_civic_action_vertical_slice
from src.storage.artifact_blob_factory import create_artifact_blob_store
from src.storage.repositories.case_content import InMemoryCaseContentRepository
from src.platform.composition import (
    create_authority_repository,
    create_case_repository,
    create_consent_repository,
    create_document_artifact_repository_for_platform,
    create_evidence_repository,
    create_identity_link_repository,
    create_provider_composition,
)
from src.platform.composition_capabilities import (
    create_authority_capability,
    create_case_capability,
    create_civic_action_capability,
    create_letter_drafting_capability,
    create_consent_capability,
    create_document_review_repository_for_platform,
)

from src.platform.surface_repository_graph import get_or_create as _get_or_create, provider_runtime_graph as _provider_runtime_graph

class FailClosedSubmissionTransport(SubmissionTransport):
    """Shared default transport that prevents unconfigured external delivery."""

    def send(self, *, case, document_id: str, destination_ref: str):
        raise RuntimeError("Submission transport is not configured; no external delivery was attempted")


@dataclass(frozen=True)
class SurfaceCaseComposition:
    """Canonical shared Case dependency graph consumed by access surfaces."""

    case_repository: object
    authority_repository: object
    evidence_repository: object
    consent_repository: object
    case_capability: CivicCaseCapability
    authority_capability: AuthorityCapability
    evidence_capability: EvidenceCapability
    consent_capability: ConsentCapability
    civic_action_capability: CivicActionCapability
    civic_action: CivicActionCapability
    letter_drafting_capability: LetterDraftingCapability
    identity_link_repository: ExternalIdentityLinkRepository
    provider_composition: object
    document_review_capability: DocumentReviewCapability
    civic_action_vertical_slice: object


def create_surface_case_composition(
    *,
    case_repository: object | None = None,
    authority_repository: object | None = None,
    evidence_repository: object | None = None,
    consent_repository: object | None = None,
    identity_link_repository: ExternalIdentityLinkRepository | None = None,
    provider_composition=None,
    document_review_repository=None,
    artifact_repository=None,
    blob_store=None,
    case_content_repository=None,
) -> SurfaceCaseComposition:
    """Compose one provider graph for an access surface.

    A single ProviderComposition is resolved first and all omitted repositories
    are derived from that same provider graph. Explicit repository injection is
    retained for deterministic tests and deployments with pre-built providers.
    """
    provider_composition = provider_composition or create_provider_composition()
    runtime_graph = _provider_runtime_graph(provider_composition)
    case_repository = case_repository or _get_or_create(
        runtime_graph, "civic_case",
        lambda: create_case_repository(provider_composition=provider_composition),
    )
    authority_repository = authority_repository or _get_or_create(
        runtime_graph, "authority",
        lambda: create_authority_repository(provider_composition=provider_composition),
    )
    evidence_repository = evidence_repository or _get_or_create(
        runtime_graph, "evidence",
        lambda: create_evidence_repository(provider_composition=provider_composition),
    )
    consent_repository = consent_repository or _get_or_create(
        runtime_graph, "consent",
        lambda: create_consent_repository(provider_composition=provider_composition),
    )
    artifact_repository = artifact_repository or _get_or_create(
        runtime_graph, "document_artifacts",
        lambda: create_document_artifact_repository_for_platform(
            provider_composition=provider_composition
        ),
    )
    blob_store = blob_store or _get_or_create(
        runtime_graph, "artifact_blob", create_artifact_blob_store
    )
    identity_link_repository = identity_link_repository or _get_or_create(
        runtime_graph, "external_identity_links",
        lambda: create_identity_link_repository(provider_composition=provider_composition),
    )

    # Citizen-authored content is surface-local by design; durable Case state is shared,
    # but sensitive narrative/claims never become shared provider state.
    if case_content_repository is None:
        # Content remains an explicit privacy/persistence boundary. Do not silently
        # promote citizen-authored narrative into the shared provider graph until a
        # durable content provider with its own retention/RLS contract is deliberately
        # selected by the runtime.
        case_content_repository = InMemoryCaseContentRepository()
    case_capability = create_case_capability(case_repository, content_repository=case_content_repository)
    authority_capability = create_authority_capability(authority_repository)
    evidence_capability = EvidenceCapability(evidence_repository, case_capability)
    consent_capability = create_consent_capability(
        consent_repository=consent_repository,
        case_capability=case_capability,
    )
    review_repository = document_review_repository or _get_or_create(
        runtime_graph, "document_review",
        lambda: create_document_review_repository_for_platform(
            provider_composition=provider_composition
        ),
    )
    document_review_capability = DocumentReviewCapability(review_repository, case_capability=case_capability)
    civic_action_capability = create_civic_action_capability(
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        case_capability=case_capability,
    )
    letter_drafting_capability = create_letter_drafting_capability(civic_action_capability, document_review_capability)
    civic_action_vertical_slice = create_civic_action_vertical_slice(
        case_repository=case_repository,
        authority_repository=authority_repository,
        consent_repository=consent_repository,
        case_capability=case_capability,
        evidence_repository=evidence_repository,
        document_review_repository=review_repository,
        letter_drafting_capability=letter_drafting_capability,
        provider_composition=provider_composition,
        artifact_repository=artifact_repository,
        blob_store=blob_store,
        submission_transport=None,
    )
    return SurfaceCaseComposition(
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        consent_repository=consent_repository,
        case_capability=case_capability,
        authority_capability=authority_capability,
        evidence_capability=evidence_capability,
        consent_capability=consent_capability,
        civic_action_capability=civic_action_capability,
        civic_action=civic_action_vertical_slice,
        letter_drafting_capability=letter_drafting_capability,
        identity_link_repository=identity_link_repository,
        provider_composition=provider_composition,
        document_review_capability=document_review_capability,
        civic_action_vertical_slice=civic_action_vertical_slice,
    )
