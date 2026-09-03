"""Canonical document artifact service."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.documents.artifact_ref import ArtifactState, DocumentArtifactRef
from src.documents.document_contract import DocumentDraft, DocumentFormat
from src.documents.renderers import render_document
from src.storage.artifact_blob import ArtifactBlobStore, StoredArtifact
from src.storage.local_artifact_blob import LocalArtifactBlobStore


@dataclass(frozen=True)
class DocumentArtifact:
    """Generated artifact intended for user review/download."""

    document_id: str
    case_id: str
    format: DocumentFormat
    path: str
    reference: DocumentArtifactRef
    stored: StoredArtifact | None = None


def generate_artifact(
    draft: DocumentDraft,
    document_format: DocumentFormat,
    output_dir: str | Path,
    *,
    blob_store: ArtifactBlobStore | None = None,
) -> DocumentArtifact:
    """Render, store and describe an artifact without transmitting it."""
    path = render_document(draft, document_format, output_dir)
    content = Path(path).read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    store = blob_store or LocalArtifactBlobStore(Path(output_dir) / "blobs")
    stored = store.put(
        f"{draft.case_id}/{draft.document_id}.{document_format.value}",
        content,
        media_type=_media_type(document_format),
    )
    if stored.content_sha256 != digest:
        raise ValueError("Artifact blob integrity verification failed")

    artifact_id = f"{draft.document_id}:{document_format.value}"
    reference = DocumentArtifactRef(
        artifact_id=artifact_id,
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format.value,
        storage_ref=stored.storage_ref,
        content_sha256=stored.content_sha256,
        state=ArtifactState.GENERATED,
    )
    return DocumentArtifact(
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format,
        path=stored.storage_ref,
        reference=reference,
        stored=stored,
    )


def _media_type(document_format: DocumentFormat) -> str:
    if document_format is DocumentFormat.PDF:
        return "application/pdf"
    if document_format is DocumentFormat.DOCX:
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    raise ValueError(f"Unsupported document format: {document_format}")
