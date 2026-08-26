"""Shared, channel-neutral document capability boundary.

The capability owns orchestration contracts only. Concrete document builders and
format renderers remain replaceable implementations. No interface (Web,
Telegram, mobile, etc.) should depend on a renderer directly.
"""

from __future__ import annotations

from typing import Callable, Mapping, Protocol

from src.documents.document_contract import (
    DocumentArtifact,
    DocumentRequest,
    StructuredDocument,
)
from src.documents.renderer import DocumentRenderer


class DocumentBuilder(Protocol):
    """Build a structured document from an authorized request."""

    def build(self, request: DocumentRequest) -> StructuredDocument:
        ...


class DocumentCapability:
    """Reusable document capability exposed to any independent interface."""

    name = "document"

    def __init__(
        self,
        builder: DocumentBuilder,
        renderers: Mapping[str, DocumentRenderer],
    ) -> None:
        self._builder = builder
        self._renderers = dict(renderers)

    def build(self, request: DocumentRequest) -> StructuredDocument:
        """Create the channel-neutral structured document."""
        return self._builder.build(request)

    def render(
        self,
        document: StructuredDocument,
        format: str,
    ) -> DocumentArtifact:
        """Render through the selected provider without exposing it to callers."""
        normalized = format.strip().lower()
        renderer = self._renderers.get(normalized)
        if renderer is None:
            raise ValueError(f"No document renderer registered for: {format}")
        return renderer.render(document)

    def supported_formats(self) -> tuple[str, ...]:
        """Return deterministic list of formats exposed by this capability."""
        return tuple(sorted(self._renderers))


__all__ = ["DocumentBuilder", "DocumentCapability"]
