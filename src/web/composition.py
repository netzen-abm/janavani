"""Web composition boundary for the canonical civic-action capability slice.

The HTTP adapter receives shared capabilities from this module rather than
constructing parallel Case, review, consent, or submission paths.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.capabilities.civic_action_vertical_slice import CivicActionVerticalSlice
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.submission import SubmissionTransport
from src.platform.composition import create_civic_action_vertical_slice
from src.storage.repositories.consent import ConsentRepository, InMemoryConsentRepository
from src.storage.repositories.document_review import (
    DocumentReviewRepository,
    InMemoryDocumentReviewRepository,
)


class UnconfiguredWebSubmissionTransport(SubmissionTransport):
    """Fail-closed Web transport until a real delivery adapter is configured."""

    def send(self, case, document_id: str, destination_ref: str):
        raise RuntimeError(
            "Web submission transport is not configured; no external delivery was attempted"
        )


@dataclass(frozen=True)
class WebCivicActionComposition:
    """Shared Web dependencies and the canonical civic-action slice."""

    case_repository: object
    consent_repository: ConsentRepository
    document_review_repository: DocumentReviewRepository
    case_capability: CivicCaseCapability
    civic_action: CivicActionVerticalSlice


def create_web_civic_action_composition(
    *,
    case_repository,
    authority_repository,
    evidence_repository=None,
    consent_repository: ConsentRepository | None = None,
    document_review_repository: DocumentReviewRepository | None = None,
    artifact_repository=None,
    blob_store=None,
    submission_transport: SubmissionTransport | None = None,
) -> WebCivicActionComposition:
    """Build the Web adapter's one canonical civic-action dependency graph.

    The default submission transport is deliberately fail-closed. A Web
    request therefore cannot claim external delivery merely because the route
    exists. Durable consent/review providers must be injected when the Web
    deployment is configured for production persistence.
    """
    consent_repo = consent_repository or InMemoryConsentRepository()
    review_repo = document_review_repository or InMemoryDocumentReviewRepository()
    transport = submission_transport or UnconfiguredWebSubmissionTransport()
    civic_action = create_civic_action_vertical_slice(
        case_repository=case_repository,
        authority_repository=authority_repository,
        consent_repository=consent_repo,
        submission_transport=transport,
        evidence_repository=evidence_repository,
        document_review_repository=review_repo,
        artifact_repository=artifact_repository,
        blob_store=blob_store,
    )
    return WebCivicActionComposition(
        case_repository=case_repository,
        consent_repository=consent_repo,
        document_review_repository=review_repo,
        case_capability=civic_action._deps.case_capability,
        civic_action=civic_action,
    )
