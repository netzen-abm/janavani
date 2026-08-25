"""Concrete PDF renderer for the channel-neutral document contract."""

from __future__ import annotations

import html
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from documents.document_contract import DocumentArtifact, StructuredDocument


def _lines(document: StructuredDocument) -> list[str]:
    content = document.content
    user = content.get("user", {})
    return [
        document.document_type.upper(),
        f"Document ID: {document.document_id}",
        f"Date: {content.get('date', document.created_on.isoformat())}",
        "",
        f"From: {user.get('name', '')}",
        str(user.get("address", "")),
        "",
        f"Office ID: {content.get('office_id', '')}",
        "",
        str(content.get("issue", "")),
    ]


class PdfRenderer:
    format = "pdf"
    media_type = "application/pdf"

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
            topMargin=20 * mm, bottomMargin=20 * mm,
        )
        styles = getSampleStyleSheet()
        story = []
        for line in _lines(document):
            story.append(
                Spacer(1, 8) if not line
                else Paragraph(html.escape(line), styles["Normal"])
            )
        pdf.build(story)
        return DocumentArtifact(
            document_id=document.document_id,
            format=self.format,
            media_type=self.media_type,
            content=buffer.getvalue(),
            filename=f"{document.document_id}.pdf",
        )
