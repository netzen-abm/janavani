"""Canonical document artifact service."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.documents.document_contract import DocumentDraft, DocumentFormat
from src.documents.renderers import render_document


@dataclass(frozen=True)
class DocumentArtifact:
    """A generated artifact intended for user review/download."""

    document_id: str
    case_id: str
    format: DocumentFormat
    path: str


def generate_artifact(
    draft: DocumentDraft,
    document_format: DocumentFormat,
    output_dir: str | Path,
) -> DocumentArtifact:
    """Generate an artifact without transmitting it anywhere."""
    path = render_document(draft, document_format, output_dir)
    return DocumentArtifact(
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format,
        path=str(path),
    )
