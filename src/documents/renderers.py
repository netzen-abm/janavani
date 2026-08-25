"""Renderer registry for independently replaceable document formats."""

from __future__ import annotations

from documents.docx_renderer import DocxRenderer
from documents.pdf_renderer import PdfRenderer
from documents.renderer import DocumentRenderer


class RendererRegistry:
    """Resolve a renderer by declared output format."""

    def __init__(self, *, register_defaults: bool = True) -> None:
        self._renderers: dict[str, DocumentRenderer] = {}
        if register_defaults:
            self.register(PdfRenderer())
            self.register(DocxRenderer())

    def register(self, renderer: DocumentRenderer) -> None:
        key = renderer.format.strip().lower()
        if not key:
            raise ValueError("renderer.format must not be empty")
        self._renderers[key] = renderer

    def get(self, format: str) -> DocumentRenderer:
        key = format.strip().lower()
        try:
            return self._renderers[key]
        except KeyError as exc:
            raise ValueError(f"No renderer registered for format: {format}") from exc

    def formats(self) -> tuple[str, ...]:
        return tuple(sorted(self._renderers))
