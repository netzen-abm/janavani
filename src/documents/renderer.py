"""Canonical document renderer contract.

Concrete renderers live in dedicated provider/format modules. This module is
intentionally limited to the shared contract so there is one ownership point
for the renderer interface and no duplicate PDF/DOCX implementations.
"""

from __future__ import annotations

from typing import Protocol

from src.documents.document_contract import DocumentArtifact, StructuredDocument


class DocumentRenderer(Protocol):
    """Contract implemented by PDF, DOCX, HTML, or future renderers."""

    format: str
    media_type: str

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        """Render a structured document into an independent artifact."""
        ...


__all__ = ["DocumentRenderer"]
