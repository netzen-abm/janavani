"""Compatibility facade for the canonical document rendering capability.

New code should use ``src.documents.renderers`` and ``DocumentDraft`` directly.
The legacy class remains temporarily so older consumers can migrate safely.
"""
from __future__ import annotations

import io
from tempfile import TemporaryDirectory

from src.documents.document_contract import DocumentDraft, DocumentFormat, DocumentParty
from src.documents.renderers import render_document


def _legacy_draft(text_content: str) -> DocumentDraft:
    """Wrap raw legacy text in the canonical document contract."""
    return DocumentDraft(
        document_id="legacy-document",
        document_type="legacy",
        case_id="legacy-case",
        date="",
        subject="Generated document",
        body=text_content,
        to=DocumentParty(name="User-selected authority", address=""),
    )


class MultiFormatDocumentEngine:
    """Compatibility facade; it renders only and never dispatches documents."""

    @staticmethod
    def _render(text_content: str, document_format: DocumentFormat) -> io.BytesIO:
        draft = _legacy_draft(text_content)
        with TemporaryDirectory(prefix="janavani-document-") as directory:
            path = render_document(draft, document_format, directory)
            return io.BytesIO(path.read_bytes())

    @staticmethod
    def generate_pdf_stream(text_content: str) -> io.BytesIO:
        """Render a legacy text payload as a PDF stream."""
        return MultiFormatDocumentEngine._render(text_content, DocumentFormat.PDF)

    @staticmethod
    def generate_docx_stream(text_content: str) -> io.BytesIO:
        """Render a legacy text payload as a DOCX stream."""
        return MultiFormatDocumentEngine._render(text_content, DocumentFormat.DOCX)
