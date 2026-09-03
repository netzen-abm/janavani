"""Local filesystem artifact blob provider for development and tests."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

from src.storage.artifact_blob import StoredArtifact


class LocalArtifactBlobStore:
    """Reference blob provider; replaceable without changing capabilities."""

    def __init__(self, root: str | Path = "/tmp/janavani-artifacts") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(
        self,
        storage_key: str,
        content: bytes | BinaryIO,
        *,
        media_type: str,
    ) -> StoredArtifact:
        path = self.root / storage_key
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with path.open("wb") as handle:
            if isinstance(content, bytes):
                handle.write(content)
                digest.update(content)
                size = len(content)
            else:
                for chunk in iter(lambda: content.read(1024 * 1024), b""):
                    handle.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
        return StoredArtifact(
            storage_ref=str(path),
            content_sha256=digest.hexdigest(),
            size_bytes=size,
            media_type=media_type,
        )

    def open(self, storage_ref: str) -> BinaryIO:
        return open(storage_ref, "rb")

    def delete(self, storage_ref: str) -> None:
        path = Path(storage_ref)
        if path.exists():
            path.unlink()
