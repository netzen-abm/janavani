"""Shared document rendering orchestration.

Rendering accepts only an already reviewed DocumentDraft and an explicit user
selected format. It performs no delivery, submission, email, database lookup,
or additional personal-data collection.
"""

from pathlib import Path

from src.core.capabilities.document_preparation import DocumentDraft
from src.core.contracts.document_rendering import DocumentFormat, DocumentRenderer, RenderedDocument


class SharedDocumentRendering:
    """Select a user-requested renderer without adding delivery behavior."""

    def __init__(self, renderers: list[DocumentRenderer]):
        self._renderers = {renderer.format: renderer for renderer in renderers}

    def render(self, draft: DocumentDraft, fmt: DocumentFormat, output_path: str) -> RenderedDocument:
        if not draft.editable:
            raise ValueError("document draft is not renderable")
        if draft.submission_enabled:
            raise ValueError("document submission must remain disabled")
        if not isinstance(fmt, DocumentFormat):
            raise ValueError("document format must be explicitly selected")
        renderer = self._renderers.get(fmt)
        if renderer is None:
            raise ValueError(f"Unsupported document format: {fmt.value}")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        return renderer.render(draft, output_path)
