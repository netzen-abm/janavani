"""Provider-neutral blob storage contract for user-owned artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Protocol


@dataclass(frozen=True)
class StoredArtifact:
    """Provider-independent location and integrity metadata."""

    storage_ref: str
    content_sha256: str
    size_bytes: int
    media_type: str


class ArtifactBlobStore(Protocol):
    """Store and retrieve bytes without owning document or case logic."""

    def put(
        self,
        storage_key: str,
        content: bytes | BinaryIO,
        *,
        media_type: str,
    ) -> StoredArtifact:
        """Persist artifact bytes and return portable metadata."""
        ...

    def open(self, storage_ref: str) -> BinaryIO:
        """Open a stored artifact for user delivery/download."""
        ...

    def delete(self, storage_ref: str) -> None:
        """Delete an artifact only when lifecycle policy permits it."""
        ...
