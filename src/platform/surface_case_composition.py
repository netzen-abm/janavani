"""Shared Case composition for independent access surfaces.

WebApp and Telegram are adapters over the same provider-neutral Case,
Evidence, Authority and Consent capabilities. This module contains no
surface-specific behavior and does not make one surface depend on another.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.capabilities.authority import AuthorityCapability
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.evidence import EvidenceCapability
from src.platform.composition import (
    create_authority_repository,
    create_case_repository,
    create_consent_repository,
    create_development_evidence_repository,
)
from src.platform.composition_capabilities import (
    create_authority_capability,
    create_case_capability,
    create_civic_action_capability,
    create_consent_capability,
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


def create_surface_case_composition() -> SurfaceCaseComposition:
    """Compose one provider-neutral Case graph for an application process."""
    case_repository = create_case_repository()
    authority_repository = create_authority_repository()
    evidence_repository = create_development_evidence_repository()
    consent_repository = create_consent_repository()

    case_capability = create_case_capability(case_repository)
    authority_capability = create_authority_capability(authority_repository)
    evidence_capability = EvidenceCapability(evidence_repository, case_capability)
    consent_capability = create_consent_capability(
        consent_repository=consent_repository,
        case_capability=case_capability,
    )
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
    )
