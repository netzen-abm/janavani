"""Entry point for supported structured civic-document generation."""
from __future__ import annotations

from documents.complaint_builder import build_complaint


class DocumentEngine:
    """Dispatch to the existing builder for supported document types."""

    def generate(self, document_type: str, **kwargs):
        """Generate a structured document or reject an unsupported type."""
        if document_type.strip().lower() == "complaint":
            return build_complaint(**kwargs)
        raise ValueError(f"Unsupported document type: {document_type}")
