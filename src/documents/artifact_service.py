"""Canonical document artifact service."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.documents.artifact_ref import ArtifactState, DocumentArtifactRef
from src.documents.document_contract import DocumentDraft, DocumentFormat
from src.documents.renderers import render_document


@dataclass(frozen=True)
class DocumentArtifact:
    """Generated artifact intended for user review/download."""

    document_id: str
    case_id: str
    format: DocumentFormat
    path: str
    reference: DocumentArtifactRef


def generate_artifact(
    draft: DocumentDraft,
    document_format: DocumentFormat,
    output_dir: str | Path,
) -> DocumentArtifact:
    """Generate an artifact without transmitting it anywhere."""
    path = render_document(draft, document_format, output_dir)
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    artifact_id = f"{draft.document_id}:{document_format.value}"
    reference = DocumentArtifactRef(
        artifact_id=artifact_id,
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format.value,
        storage_ref=str(path),
        content_sha256=digest,
        state=ArtifactState.GENERATED,
    )
    return DocumentArtifact(
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format,
        path=str(path),
        reference=reference,
    )
