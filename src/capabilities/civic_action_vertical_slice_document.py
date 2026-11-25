"""Document preparation, review and artifact helpers for the civic-action slice."""
from __future__ import annotations
from pathlib import Path
from src.capabilities.document_review import DocumentReviewRequest
from src.capabilities.letter_drafting import LetterDraftRequest
from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentFormat
from src.documents.artifact_ref import ArtifactState
from src.identity.context import IdentityContext
from src.storage.repositories.artifact_provider import create_document_artifact_repository

class CivicActionDocuments:
    def __init__(self, deps): self._deps = deps

    @staticmethod
    def _jurisdiction_label(jurisdiction: dict[str, object]) -> str | None:
        values = [
            str(value).strip()
            for value in jurisdiction.values()
            if value is not None and str(value).strip()
        ]
        return ", ".join(values) or None

    def prepare(
        self,
        case_id: str,
        *,
        identity: IdentityContext,
        document_id=None,
        draft_request: LetterDraftRequest | None = None,
    ):
        case = self._deps.case_capability.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        if draft_request is None:
            case_type = getattr(case.case_type, "value", case.case_type)
            template_ids = {
                "complaint": "complaint.general",
                "corruption": "complaint.general",
                "misbehaviour": "complaint.general",
                "transfer_concern": "complaint.general",
                "other": "complaint.general",
                "grievance": "grievance.service",
                "rti": "rti.records",
                "petition": "petition.general",
                "appeal": "petition.general",
                "representation": "representation.general",
                "objection": "representation.general",
                "non_consent": "representation.general",
            }
            template_id = template_ids.get(str(case_type))
            if template_id is None:
                raise ValueError("No approved drafting template is mapped to this Case type")
            draft_request = LetterDraftRequest(
                subject=case.subject,
                issue=case.narrative,
                evidence_refs=tuple(case.evidence_refs),
                jurisdiction=self._jurisdiction_label(case.jurisdiction),
                template_id=template_id,
            )
        result = self._deps.letter_drafting_capability.create_draft(
            case_id,
            draft_request,
            identity=identity,
            document_id=document_id,
        )
        return result.document

    def review(self, request: DocumentReviewRequest, *, identity: IdentityContext):
        return self._deps.document_review_capability.edit(request, identity=identity)

    def start_review(self, case_id: str, *, identity: IdentityContext):
        return self._deps.case_capability.start_review(case_id, identity=identity)

    def approve(self, case_id: str, *, identity: IdentityContext):
        return self._deps.case_capability.approve(case_id, identity=identity)

    def open_artifact(self, artifact_id: str, *, case_id: str, identity: IdentityContext):
        repository = self._deps.artifact_repository or create_document_artifact_repository()
        artifact = repository.get(artifact_id)
        if artifact is None or artifact.case_id != case_id or artifact.state is not ArtifactState.USER_APPROVED:
            raise LookupError("Document artifact not found")
        case = self._deps.case_capability.get_owned(case_id, identity=identity)
        if case is None or artifact_id not in case.document_refs:
            raise LookupError("Document artifact not found")
        if self._deps.blob_store is None:
            raise RuntimeError("Artifact blob storage is not configured")
        return artifact, self._deps.blob_store.open(artifact.storage_ref)

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
