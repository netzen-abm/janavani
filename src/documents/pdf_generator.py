"""Compatibility facade for the former standalone PDF generator.

Canonical rendering lives in ``documents.renderers.DocumentRenderer``.
"""

from documents.renderers import DocumentRenderer


class PDFGenerator:
    """Legacy file-path facade over the canonical PDF renderer."""

    def generate(self, text: str, output_file: str) -> str:
        artifact = DocumentRenderer.pdf({"title": "JANAVANI DOCUMENT", "content": text})
        with open(output_file, "wb") as handle:
            handle.write(artifact.content)
        return output_file
