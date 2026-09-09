"""Canonical end-to-end civic-action orchestration boundary.

This module composes existing provider- and surface-neutral capabilities. It does
not own Case, Evidence, Authority, Document, Consent, or Submission semantics.
Access surfaces should use this orchestration boundary rather than rebuilding
the civic-action lifecycle themselves.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.capabilities.document_review import DocumentReviewCapability, DocumentReviewRequest
from src.capabilities.submission import SubmissionCapability, SubmissionRequest
from src.core.evidence import EvidenceRepository
from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentDraft, DocumentFormat
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
    document_review_capability: DocumentReviewCapability
    submission_capability: SubmissionCapability
    case_repository: CivicCaseRepository
    document_review_repository: DocumentReviewRepository
    artifact_repository: DocumentArtifactRepository | None = None
    blob_store: ArtifactBlobStore | None = None
    evidence_repository: EvidenceRepository | None = None


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

    def prepare_document(self, case_id: str, *, identity: IdentityContext,
                         document_id: str | None = None) -> PreparedDocument:
        """Resolve Case → Evidence → Authority and persist the reviewable draft."""
        result = self._deps.civic_action_capability.build_document(
            case_id, identity=identity, document_id=document_id
        )
        self._deps.document_review_repository.save(result.draft)
        self._deps.case_capability.add_document(
            case_id, result.draft.document_id, identity=identity, source_channel="shared"
        )
        return PreparedDocument(case_id=case_id, document_id=result.draft.document_id, draft=result.draft)

    def review_document(self, request: DocumentReviewRequest, *, identity: IdentityContext):
        """Apply an owner-authorized correction and record a revision."""
        return self._deps.document_review_capability.edit(request, identity=identity)

    def approve(self, case_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        """Mark the Case ready only through the canonical Case lifecycle."""
        return self._deps.case_capability.approve(case_id, identity=identity)

    def generate_artifact(self, document_id: str, *, identity: IdentityContext,
                          document_format: DocumentFormat = DocumentFormat.PDF,
                          output_dir: str | Path = "/tmp/janavani-artifacts/rendered") -> DocumentArtifact:
        """Render the latest owned reviewed draft; never submit or transmit it."""
        draft = self._deps.document_review_capability.get_owned(document_id, identity=identity)
        if draft is None:
            raise LookupError("Document draft not found")
        artifact = generate_artifact(
            draft, document_format, output_dir, blob_store=self._deps.blob_store
        )
        repository = self._deps.artifact_repository or create_document_artifact_repository()
        repository.save(artifact.reference)
        self._deps.case_capability.add_document(
            draft.case_id, artifact.reference.artifact_id, identity=identity, source_channel="shared"
        )
        return artifact

    def submit(self, request: SubmissionRequest, *, identity: IdentityContext,
               explicit_user_approval: bool) -> CivicCaseResult:
        """Submit only through the canonical approval/consent/transport boundary."""
        return self._deps.submission_capability.submit(
            request, identity=identity, explicit_user_approval=explicit_user_approval
        )
