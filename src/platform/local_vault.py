"""Provider-neutral contract for browser-local encrypted state.

The Python backend cannot access browser IndexedDB or Web Crypto directly. This
module therefore defines the application-level contract that a Web client must
implement locally. It deliberately stores opaque encrypted envelopes only.
"""
from __future__ import annotations

from typing import Protocol

from src.platform.encrypted_envelope import EncryptedEnvelope


class LocalVault(Protocol):
    """Minimal client-owned vault interface."""

    def put(self, key: str, envelope: EncryptedEnvelope) -> None:
        """Persist an opaque encrypted envelope locally."""
        ...

    def get(self, key: str) -> EncryptedEnvelope | None:
        """Return an opaque encrypted envelope, if present."""
        ...

    def delete(self, key: str) -> None:
        """Delete local state for a key."""
        ...

    def keys(self) -> list[str]:
        """List local record keys without exposing plaintext."""
        ...
