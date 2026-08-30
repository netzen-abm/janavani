"""Canonical document capability entry point.

DocumentEngine composes structured documents and delegates rendering to the
shared renderer. Channels and transports never own document business logic.
The final artifact format is selected explicitly by the user.
"""

from __future__ import annotations

from documents.complaint_builder import ComplaintBuilder
from documents.output_formats import OutputFormat, resolve_output_format
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
        output_format: str | OutputFormat,
        **kwargs,
    ) -> DocumentArtifact:
        """Generate the format explicitly selected by the user.

        ``pdf`` produces a PDF. ``document``/``docx`` produces an editable
        Word document. No access surface may silently choose the format.
        """

        format_spec = resolve_output_format(output_format)
        payload = self.compose(document_type, **kwargs)
        return DocumentRenderer.render(payload, format_spec.format.value)
