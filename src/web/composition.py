"""Web composition boundary for the canonical civic-action capability slice.

The HTTP adapter receives the same surface-neutral capability graph used by
other access surfaces. Web-specific behavior remains limited to HTTP concerns.
"""
from __future__ import annotations

from src.capabilities.submission import SubmissionTransport
from src.platform.surface_case_composition import (
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
    return create_surface_case_composition(
        case_repository=case_repository,
        authority_repository=authority_repository,
        evidence_repository=evidence_repository,
        consent_repository=consent_repository,
        identity_link_repository=identity_link_repository,
        provider_composition=provider_composition,
        submission_transport=submission_transport,
    )
