"""Shared Case composition for independent access surfaces.

WebApp and Telegram are adapters over the same provider-neutral Case,
Evidence, Authority and Consent capabilities. This module contains no
surface-specific behavior and does not make one surface depend on another.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.capabilities.authority import AuthorityCapability
from src.identity.linking import ExternalIdentityLinkRepository
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.platform.composition import (
    create_authority_repository,
    create_case_repository,
    create_consent_repository,
    create_evidence_repository,
    create_identity_link_repository,
    create_provider_composition,
)
from src.platform.composition_capabilities import (
    create_authority_capability,
    create_case_capability,
    create_civic_action_capability,
    create_consent_capability,
    create_document_review_repository_for_platform,
)


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
    identity_link_repository: ExternalIdentityLinkRepository
    provider_composition: object
    document_review_capability: DocumentReviewCapability


def create_surface_case_composition(
    *,
    case_repository: object | None = None,
    authority_repository: object | None = None,
    evidence_repository: object | None = None,
    consent_repository: object | None = None,
    identity_link_repository: ExternalIdentityLinkRepository | None = None,
    provider_composition=None,
) -> SurfaceCaseComposition:
    """Compose one provider graph for an access surface.

    A single ProviderComposition is resolved first and all omitted repositories
    are derived from that same provider graph. Explicit repository injection is
    retained for deterministic tests and deployments with pre-built providers.
    """
    provider_composition = provider_composition or create_provider_composition()

    case_repository = case_repository or create_case_repository(
        provider_composition=provider_composition
    )
    authority_repository = authority_repository or create_authority_repository(
        provider_composition=provider_composition
    )
    evidence_repository = evidence_repository or create_evidence_repository(
        provider_composition=provider_composition
    )
    consent_repository = consent_repository or create_consent_repository(
        provider_composition=provider_composition
    )
    identity_link_repository = identity_link_repository or create_identity_link_repository(
        provider_composition=provider_composition
    )

    case_capability = create_case_capability(case_repository)
    authority_capability = create_authority_capability(authority_repository)
    evidence_capability = EvidenceCapability(evidence_repository, case_capability)
    consent_capability = create_consent_capability(
        consent_repository=consent_repository,
        case_capability=case_capability,
    )
    review_repository = create_document_review_repository_for_platform(provider_composition=provider_composition)
    document_review_capability = DocumentReviewCapability(review_repository, case_capability=case_capability)
    civic_action_capability = create_civic_action_capability(
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        case_capability=case_capability,
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
        identity_link_repository=identity_link_repository,
        provider_composition=provider_composition,
        document_review_capability=document_review_capability,
    )
