"""Provider-neutral renderers for the canonical DocumentDraft contract."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from src.documents.document_contract import DocumentDraft, DocumentFormat


class DocumentRenderer(Protocol):
    """Render a canonical draft into a user-owned artifact."""

    def render(self, draft: DocumentDraft, output_dir: str | Path) -> Path:
        ...


def render_document(
    draft: DocumentDraft,
    document_format: DocumentFormat,
    output_dir: str | Path,
) -> Path:
    """Render PDF or DOCX without performing any delivery action."""
    if document_format is DocumentFormat.PDF:
        from src.documents.renderers_pdf import PdfDocumentRenderer

        return PdfDocumentRenderer().render(draft, output_dir)
    if document_format is DocumentFormat.DOCX:
        from src.documents.renderers_docx import DocxDocumentRenderer

        return DocxDocumentRenderer().render(draft, output_dir)
    raise ValueError(f"Unsupported document format: {document_format}")
