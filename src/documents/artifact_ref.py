"""Portable document artifact reference metadata."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ArtifactState(str, Enum):
    GENERATED = "generated"
    USER_APPROVED = "user_approved"
    DOWNLOADED = "downloaded"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class DocumentArtifactRef:
    """Durable metadata reference; it never represents external delivery."""

    artifact_id: str
    document_id: str
    case_id: str
    format: str
    storage_ref: str
    content_sha256: str | None = None
    state: ArtifactState = ArtifactState.GENERATED

    def mark_downloaded(self) -> "DocumentArtifactRef":
        return DocumentArtifactRef(
            artifact_id=self.artifact_id,
            document_id=self.document_id,
            case_id=self.case_id,
            format=self.format,
            storage_ref=self.storage_ref,
            content_sha256=self.content_sha256,
            state=ArtifactState.DOWNLOADED,
        )
