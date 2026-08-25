"""Renderer contract for channel-neutral Janavani documents.

Rendering is deliberately separate from composition and delivery. New output
formats can be plugged in without changing document builders or client code.
"""

from __future__ import annotations

from typing import Protocol

from documents.document_contract import DocumentArtifact, StructuredDocument


class DocumentRenderer(Protocol):
    """Contract implemented by PDF, DOCX, HTML, or future renderers."""

    format: str
    media_type: str

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        """Render a structured document into an independent artifact."""
