"""Canonical document artifact service."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.documents.artifact_ref import ArtifactState, DocumentArtifactRef
from src.documents.document_contract import DocumentDraft, DocumentFormat
from src.documents.renderers import render_document
from src.storage.artifact_blob import ArtifactBlobStore, StoredArtifact


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
    """Render an artifact and optionally persist bytes through a blob provider."""
    path = render_document(draft, document_format, output_dir)
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    stored = None

    if blob_store is not None:
        media_type = (
            "application/pdf"
            if document_format is DocumentFormat.PDF
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        with Path(path).open("rb") as handle:
            stored = blob_store.put(
                f"{draft.case_id}/{draft.document_id}.{document_format.value}",
                handle,
                media_type=media_type,
            )
        storage_ref = stored.storage_ref
    else:
        storage_ref = str(path)

    artifact_id = f"{draft.document_id}:{document_format.value}"
    reference = DocumentArtifactRef(
        artifact_id=artifact_id,
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format.value,
        storage_ref=storage_ref,
        content_sha256=digest,
        state=ArtifactState.GENERATED,
    )
    return DocumentArtifact(
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format,
        path=str(path),
        reference=reference,
        stored=stored,
    )
