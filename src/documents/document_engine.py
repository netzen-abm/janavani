"""Canonical document capability entry point.

DocumentEngine composes structured documents and delegates rendering to the
shared renderer. Channels and transports never own document business logic.
"""

from __future__ import annotations

from documents.complaint_builder import ComplaintBuilder
from documents.renderers import DocumentArtifact, DocumentRenderer


class DocumentEngine:
    """Stable capability facade for document composition and export."""

    def __init__(self, complaint_builder: ComplaintBuilder | None = None):
        self.complaint_builder = complaint_builder or ComplaintBuilder()

    def compose(self, document_type: str, **kwargs) -> dict:
        normalized = document_type.lower()
        if normalized == "complaint":
            return self.complaint_builder.build(**kwargs)
        raise ValueError(f"Unsupported document type: {document_type}")

    def generate(
        self,
        document_type: str,
        format_type: str = "pdf",
        **kwargs,
    ) -> DocumentArtifact:
        payload = self.compose(document_type, **kwargs)
        return DocumentRenderer.render(payload, format_type)
