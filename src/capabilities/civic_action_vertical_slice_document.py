"""Document preparation, review and artifact helpers for the civic-action slice."""
from __future__ import annotations
from pathlib import Path
from src.capabilities.document_review import DocumentReviewRequest
from src.core.execution import CapabilityExecutionContext
from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentDraft, DocumentFormat
from src.identity.context import IdentityContext
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.artifact_provider import create_document_artifact_repository

class CivicActionDocuments:
    def __init__(self, deps): self._deps = deps

    def prepare(self, case_id: str, *, identity: IdentityContext, document_id=None):
        result = self._deps.civic_action_capability.build_document(
            case_id, identity=identity, document_id=document_id
        )
        self._deps.document_review_repository.save(result.draft)
        self._deps.case_capability.add_document(
            case_id, result.draft.document_id, identity=identity, source_channel="shared"
        )
        return result.draft

    def review(self, request: DocumentReviewRequest, *, identity: IdentityContext):
        return self._deps.document_review_capability.edit(request, identity=identity)

    def start_review(self, case_id: str, *, identity: IdentityContext):
        return self._deps.case_capability.start_review(case_id, identity=identity)

    def approve(self, case_id: str, *, identity: IdentityContext):
        return self._deps.case_capability.approve(case_id, identity=identity)

    def generate(
        self, document_id: str, *, identity: IdentityContext,
        case_id: str | None = None,
        document_format: DocumentFormat = DocumentFormat.PDF,
        output_dir: str | Path = "/tmp/janavani-artifacts/rendered",
    ) -> DocumentArtifact:
        draft = self._deps.document_review_capability.get_owned(
            document_id, identity=identity
        )
        if draft is None or (case_id is not None and draft.case_id != case_id):
            raise LookupError("Document draft not found")
        artifact = generate_artifact(
            draft, document_format, output_dir, blob_store=self._deps.blob_store
        )
        repository = self._deps.artifact_repository or create_document_artifact_repository()
        repository.save(artifact.reference)
        self._deps.case_capability.add_document(
            draft.case_id, artifact.reference.artifact_id,
            identity=identity, source_channel="shared"
        )
        return artifact
