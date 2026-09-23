"""Web composition boundary for the canonical civic-action capability slice.

The HTTP adapter receives the same surface-neutral capability graph used by
other access surfaces. Web-specific behavior remains limited to HTTP concerns.
"""
from __future__ import annotations

from src.capabilities.submission import SubmissionTransport
from src.platform.surface_case_composition import (
    FailClosedSubmissionTransport,
    SurfaceCaseComposition,
    create_surface_case_composition,
)


def create_web_civic_action_composition(
    *,
    case_repository=None,
    authority_repository=None,
    evidence_repository=None,
    consent_repository=None,
    identity_link_repository=None,
    provider_composition=None,
    submission_transport: SubmissionTransport | None = None,
) -> SurfaceCaseComposition:
    """Build the Web adapter's canonical surface-neutral dependency graph.

    Repository and capability ownership deliberately lives in the shared
    platform composition boundary. Web may inject deterministic providers for
    tests, but it does not own a second capability graph.
    """
    composition = create_surface_case_composition(
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        consent_repository=consent_repository,
        identity_link_repository=identity_link_repository,
        provider_composition=provider_composition,
    )
    if submission_transport is None:
        return composition

    # Keep Web transport selection at the surface adapter boundary while
    # retaining the same repository/capability graph.
    from src.platform.composition_capabilities import create_civic_action_vertical_slice

    review_repository = getattr(composition.civic_action_vertical_slice._deps, "document_review_repository", None)
    artifact_repository = getattr(composition.civic_action_vertical_slice._deps, "artifact_repository", None)
    blob_store = getattr(composition.civic_action_vertical_slice._deps, "blob_store", None)
    vertical_slice = create_civic_action_vertical_slice(
        case_repository=composition.case_repository,
        authority_repository=composition.authority_repository,
        consent_repository=composition.consent_repository,
        submission_transport=submission_transport,
        evidence_repository=composition.evidence_repository,
        document_review_repository=review_repository,
        artifact_repository=artifact_repository,
        blob_store=blob_store,
        provider_composition=composition.provider_composition,
    )
    return SurfaceCaseComposition(
        case_repository=composition.case_repository,
        authority_repository=composition.authority_repository,
        evidence_repository=composition.evidence_repository,
        consent_repository=composition.consent_repository,
        case_capability=composition.case_capability,
        authority_capability=composition.authority_capability,
        evidence_capability=composition.evidence_capability,
        consent_capability=composition.consent_capability,
        civic_action_capability=composition.civic_action_capability,
        identity_link_repository=composition.identity_link_repository,
        provider_composition=composition.provider_composition,
        document_review_capability=composition.document_review_capability,
        civic_action_vertical_slice=vertical_slice,
    )
