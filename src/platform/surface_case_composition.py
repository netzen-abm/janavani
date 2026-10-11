"""Shared Case composition for independent access surfaces.

WebApp and Telegram are adapters over the same provider-neutral Case,
Evidence, Authority and Consent capabilities. This module contains no
surface-specific behavior and does not make one surface depend on another.
"""
from __future__ import annotations

from dataclasses import dataclass
import os

from src.capabilities.authority import AuthorityCapability
from src.identity.linking import ExternalIdentityLinkRepository
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.capabilities.letter_drafting import LetterDraftingCapability
from src.capabilities.submission_contract import SubmissionTransport
from src.platform.composition_capabilities import (
    create_civic_action_vertical_slice,
    create_authority_capability,
    create_case_capability,
    create_civic_action_capability,
    create_letter_drafting_capability,
    create_consent_capability,
)
from src.storage.repositories.case_content import (
    InMemoryCaseContentRepository,
    TransientCaseContentRepository,
)


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
    from src.platform.surface_repository_graph import create_surface_repository_graph

    repositories = create_surface_repository_graph(
        provider_composition=provider_composition,
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        consent_repository=consent_repository,
        identity_link_repository=identity_link_repository,
        artifact_repository=artifact_repository,
        blob_store=blob_store,
        document_review_repository=document_review_repository,
    )
    provider_composition = repositories.provider_composition
    case_repository = repositories.case_repository
    authority_repository = repositories.authority_repository
    evidence_repository = repositories.evidence_repository
    consent_repository = repositories.consent_repository
    identity_link_repository = repositories.identity_link_repository
    artifact_repository = repositories.artifact_repository
    blob_store = repositories.blob_store

    # Citizen-authored content has its own privacy and persistence contract.
    # Never let a production process silently accept process-local-only content.
    runtime_mode = os.getenv("JANAVANI_RUNTIME_MODE", "development").strip().lower()
    content_policy = os.getenv("JANAVANI_CASE_CONTENT_POLICY", "").strip().lower()
    if case_content_repository is None:
        if content_policy == "transient":
            case_content_repository = TransientCaseContentRepository()
        elif runtime_mode == "production":
            raise ValueError(
                "Production requires an explicit CaseContentRepository or "
                "JANAVANI_CASE_CONTENT_POLICY=transient; citizen content is not "
                "durable Case metadata and must not be persisted by default"
            )
        else:
            case_content_repository = InMemoryCaseContentRepository()
    elif runtime_mode == "production" and isinstance(
        case_content_repository, InMemoryCaseContentRepository
    ):
        raise ValueError(
            "InMemoryCaseContentRepository is for development/tests; use an explicitly "
            "configured durable adapter or JANAVANI_CASE_CONTENT_POLICY=transient"
        )
    elif isinstance(case_content_repository, TransientCaseContentRepository) and (
        runtime_mode == "production" and content_policy != "transient"
    ):
        raise ValueError(
            "TransientCaseContentRepository requires JANAVANI_CASE_CONTENT_POLICY=transient"
        )
    case_capability = create_case_capability(case_repository, content_repository=case_content_repository)
    authority_capability = create_authority_capability(authority_repository)
    evidence_capability = EvidenceCapability(evidence_repository, case_capability)
    consent_capability = create_consent_capability(
        consent_repository=consent_repository,
        case_capability=case_capability,
    )
    review_repository = repositories.document_review_repository
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
