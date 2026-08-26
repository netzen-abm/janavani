"""Concrete DOCX renderer for the channel-neutral document contract."""

from __future__ import annotations

import io

from docx import Document

from src.documents.document_contract import DocumentArtifact, StructuredDocument


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


class DocxRenderer:
    format = "docx"
    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        buffer = io.BytesIO()
        doc = Document()
        for line in _lines(document):
            doc.add_paragraph(line)
        doc.save(buffer)
        return DocumentArtifact(
            document_id=document.document_id,
            format=self.format,
            media_type=self.media_type,
            content=buffer.getvalue(),
            filename=f"{document.document_id}.docx",
        )
