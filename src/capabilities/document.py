"""Shared, channel-neutral document capability.

The capability owns structured document composition and output selection. Access
surfaces only provide user-approved data and the user's requested format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from documents.output_formats import OutputFormat, resolve_output_format
from documents.renderers import DocumentArtifact, DocumentRenderer

SUPPORTED_TYPES = {"complaint", "grievance", "rti", "petition", "representation", "objection"}


@dataclass(frozen=True)
class DocumentPayload:
    case_id: str
    document_type: str
    version: str
    fields: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)


class DocumentComposer(Protocol):
    def compose(self, payload: DocumentPayload) -> dict[str, Any]: ...


class SharedDocumentCapability:
    """Compose once; render the same payload in the user's selected format."""

    def __init__(self, composers: dict[str, DocumentComposer] | None = None):
        self._composers = composers or {}

    def register(self, document_type: str, composer: DocumentComposer) -> None:
        self._composers[document_type.lower()] = composer

    def compose(self, payload: DocumentPayload) -> dict[str, Any]:
        document_type = payload.document_type.lower()
        if document_type not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported document type: {payload.document_type}")
        composer = self._composers.get(document_type)
        if composer is None:
            raise RuntimeError(f"No composer registered for {document_type}")
        return composer.compose(payload)

    def generate(self, payload: DocumentPayload, output_format: str | OutputFormat) -> DocumentArtifact:
        spec = resolve_output_format(output_format)
        structured = self.compose(payload)
        artifact = DocumentRenderer.render(structured, spec.format.value)
        if artifact.extension != spec.extension or artifact.media_type != spec.media_type:
            raise RuntimeError("Renderer returned a format different from the user's selection")
        return artifact
