"""Provider-neutral document artifact persistence boundary."""
from __future__ import annotations

from typing import Protocol

from src.documents.artifact_ref import DocumentArtifactRef


class DocumentArtifactRepository(Protocol):
    """Durable artifact metadata contract, independent of blob storage."""

    def save(self, artifact: DocumentArtifactRef) -> None:
        """Persist artifact metadata and its lifecycle state."""
        ...

    def get(self, artifact_id: str) -> DocumentArtifactRef | None:
        """Return an artifact by identifier when present."""
        ...

    def list_for_case(self, case_id: str) -> list[DocumentArtifactRef]:
        """Return artifacts associated with a civic case."""
        ...


class InMemoryDocumentArtifactRepository:
    """Reference implementation for tests and local development."""

    def __init__(self) -> None:
        self._items: dict[str, DocumentArtifactRef] = {}

    def save(self, artifact: DocumentArtifactRef) -> None:
        self._items[artifact.artifact_id] = artifact

    def get(self, artifact_id: str) -> DocumentArtifactRef | None:
        return self._items.get(artifact_id)

    def list_for_case(self, case_id: str) -> list[DocumentArtifactRef]:
        return [
            artifact
            for artifact in self._items.values()
            if artifact.case_id == case_id
        ]
