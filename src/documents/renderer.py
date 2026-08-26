"""Canonical document renderer contracts and implementations.

Rendering consumes a StructuredDocument and returns a channel-neutral
DocumentArtifact. Rendering does not own composition, persistence, delivery,
or channel integration.
"""

from __future__ import annotations

import io
from typing import Any, Protocol

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.documents.document_contract import DocumentArtifact, StructuredDocument


class DocumentRenderer(Protocol):
    """Contract implemented by PDF, DOCX, HTML, or future renderers."""

    format: str
    media_type: str

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        """Render a structured document into an independent artifact."""


class PDFDocumentRenderer:
    """Render a structured Janavani document as PDF bytes."""

    format = "pdf"
    media_type = "application/pdf"

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54,
        )
        styles = getSampleStyleSheet()
        body = ParagraphStyle(
            "JanavaniBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            spaceAfter=10,
        )

        story: list[Any] = []
        for line in _document_text_lines(document):
            if not line:
                story.append(Spacer(1, 12))
            else:
                story.append(Paragraph(line, body))
        pdf.build(story)

        return DocumentArtifact(
            document_id=document.document_id,
            format=self.format,
            media_type=self.media_type,
            content=buffer.getvalue(),
            filename=f"{document.document_id}.pdf",
        )


class DOCXDocumentRenderer:
    """Render a structured Janavani document as editable DOCX bytes."""

    format = "docx"
    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        buffer = io.BytesIO()
        doc = Document()
        for line in _document_text_lines(document):
            doc.add_paragraph(line)
        doc.save(buffer)

        return DocumentArtifact(
            document_id=document.document_id,
            format=self.format,
            media_type=self.media_type,
            content=buffer.getvalue(),
            filename=f"{document.document_id}.docx",
        )


def _document_text_lines(document: StructuredDocument) -> list[str]:
    """Flatten current structured content without inventing legal content."""

    lines: list[str] = []
    for value in document.content.values():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            lines.extend(str(item) for item in value)
        else:
            lines.append(str(value))
    return lines
