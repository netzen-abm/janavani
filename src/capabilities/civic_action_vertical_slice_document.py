"""Document preparation, review and artifact helpers for the civic-action slice."""
from __future__ import annotations
from dataclasses import dataclass, replace
from pathlib import Path
from src.capabilities.document_review import DocumentReviewRequest
from src.core.execution import CapabilityExecutionContext
from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentDraft, DocumentFormat
from src.documents.artifact_ref import ArtifactState
from src.identity.context import IdentityContext
from src.core.case_types import CaseStatus
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.artifact_provider import create_document_artifact_repository

@dataclass(frozen=True)
class DocumentPackageItem:
    """One citizen-reviewable petition or RTI with its downloadable artifacts."""

    document_type: str
    draft: DocumentDraft
    artifacts: tuple[DocumentArtifact, ...]


@dataclass(frozen=True)
class DocumentPackage:
    """Citizen-delivery package containing one or more reviewed document types."""

    case_id: str
    items: tuple[DocumentPackageItem, ...]
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

    def generate_package(
        self, case_id: str, *, identity: IdentityContext,
        document_types: tuple[str, ...] = ("petition",),
        formats: tuple[DocumentFormat, ...] = (
            DocumentFormat.PDF, DocumentFormat.DOCX,
        ), output_dir: str | Path = "/tmp/janavani-artifacts/rendered",
    ) -> DocumentPackage:
        """Prepare one or both citizen-delivery document types; never transmit."""
        selected_types = tuple(dict.fromkeys(document_types))
        if not selected_types or any(item not in {"petition", "rti"} for item in selected_types):
            raise ValueError("document_types must contain petition, rti, or both")
        case = self._deps.civic_action_capability.build_document(case_id, identity=identity).case
        if case.status is not CaseStatus.READY:
            raise ValueError("Final document artifacts require an approved case review")
        items = []
        for document_type in selected_types:
            result = self._deps.civic_action_capability.build_document(case_id, identity=identity)
            from src.documents.document_contract import DocumentParty
            draft = DocumentDraft(
                document_id=f"{result.draft.document_id}-{document_type}",
                document_type=document_type,
                case_id=result.draft.case_id,
                date=result.draft.date,
                subject=result.draft.subject,
                body=result.draft.body,
                to=result.draft.to,
                cc=result.draft.cc,
                sender=result.draft.sender or DocumentParty(
                    name="[YOUR NAME]",
                    address="[YOUR FULL POSTAL ADDRESS]",
                    email="[YOUR EMAIL ADDRESS]",
                    role="Applicant — fill before sending",
                ),
                legal_ground=result.draft.legal_ground,
            )
            self._deps.document_review_repository.save(draft)
            artifacts = tuple(
                generate_artifact(draft, fmt, output_dir, blob_store=self._deps.blob_store)
                for fmt in formats
            )
            repository = self._deps.artifact_repository or create_document_artifact_repository()
            approved_artifacts = tuple(
                replace(artifact, reference=replace(artifact.reference, state=ArtifactState.USER_APPROVED))
                for artifact in artifacts
            )
            for artifact in approved_artifacts:
                repository.save(artifact.reference)
                self._deps.case_capability.add_document(
                    case_id, artifact.reference.artifact_id,
                    identity=identity, source_channel="shared",
                )
            items.append(DocumentPackageItem(
                document_type=document_type, draft=draft, artifacts=approved_artifacts
            ))
        return DocumentPackage(case_id=case.case_id, items=tuple(items))
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
