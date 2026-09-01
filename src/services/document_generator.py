"""Compatibility facade for the shared document renderer.

New code should depend on ``documents.document_engine.DocumentEngine`` or
``documents.renderers.DocumentRenderer``. This module remains temporarily to
avoid breaking older transport adapters during ecosystem migration.
"""

from documents.renderers import DocumentRenderer


class MultiFormatDocumentEngine:
    """Backward-compatible adapter returning in-memory PDF/DOCX streams."""

    @staticmethod
    def generate_pdf_stream(text_content: str):
        payload = {"title": "JANAVANI DOCUMENT", "content": text_content}
        artifact = DocumentRenderer.render(payload, "pdf")
        import io

        return io.BytesIO(artifact.content)

    @staticmethod
    def generate_docx_stream(text_content: str):
        payload = {"title": "JANAVANI DOCUMENT", "content": text_content}
        artifact = DocumentRenderer.render(payload, "docx")
        import io

        return io.BytesIO(artifact.content)
