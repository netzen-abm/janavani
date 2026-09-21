"""Web composition boundary for the canonical civic-action capability slice.

The HTTP adapter receives shared capabilities from this module rather than
constructing parallel Case, review, consent, or submission paths.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.capabilities.civic_action_vertical_slice import CivicActionVerticalSlice
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.submission import SubmissionTransport
from src.capabilities.authority import AuthorityCapability
from src.capabilities.evidence import EvidenceCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.platform.composition import (
    create_authority_capability,
    create_consent_capability,
    create_authority_repository,
    create_case_repository,
    create_evidence_repository,
    create_civic_action_vertical_slice,
    create_consent_repository,
    create_document_review_repository_for_platform,
    create_provider_composition,
)
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.document_review import DocumentReviewRepository


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
    authority_capability: AuthorityCapability
    evidence_capability: EvidenceCapability
    consent_capability: ConsentCapability
    document_review_capability: DocumentReviewCapability
    civic_action: CivicActionVerticalSlice


def create_web_civic_action_composition(
    *,
    case_repository=None,
    authority_repository=None,
    evidence_repository=None,
    consent_repository: ConsentRepository | None = None,
    document_review_repository: DocumentReviewRepository | None = None,
    artifact_repository=None,
    blob_store=None,
    submission_transport: SubmissionTransport | None = None,
    provider_composition: ProviderComposition | None = None,
) -> WebCivicActionComposition:
    """Build the Web adapter's one canonical civic-action dependency graph.

    The default submission transport is deliberately fail-closed. Provider
    defaults come from the shared platform composition; durable providers can
    still be injected explicitly when a deployment has completed its
    persistence and migration readiness work.
    """
    composition = provider_composition or create_provider_composition()
    case_repository = case_repository or create_case_repository(provider_composition=composition)
    authority_repository = authority_repository or create_authority_repository(provider_composition=composition)
    evidence_repository = evidence_repository or create_evidence_repository(provider_composition=composition)
    consent_repo = consent_repository or create_consent_repository(
        provider_composition=composition
    )
    review_repo = document_review_repository or create_document_review_repository_for_platform(
        provider_composition=composition
    )
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
        provider_composition=composition,
    )
    return WebCivicActionComposition(
        case_repository=case_repository,
        consent_repository=consent_repo,
        document_review_repository=review_repo,
        case_capability=civic_action._deps.case_capability,
        authority_capability=civic_action._deps.external_channel_capability and create_authority_capability(authority_repository),
        evidence_capability=civic_action._deps.evidence_capability,
        consent_capability=civic_action._deps.case_capability and create_consent_capability(consent_repository=consent_repo, case_capability=civic_action._deps.case_capability),
        document_review_capability=civic_action._deps.document_review_capability,
        civic_action=civic_action,
    )
