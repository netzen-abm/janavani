"""Provider-neutral storage capability contract.

Storage implementations are adapters. Application/domain code should depend on
this contract rather than importing a provider SDK or singleton directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class StorageResult:
    """Channel-neutral result for a storage operation."""

    ok: bool
    value: Any = None
    error_code: str | None = None


class StorageAdapter(Protocol):
    """Minimum contract for independently replaceable storage providers."""

    def get(self, collection: str, key: str) -> StorageResult:
        """Retrieve one value without exposing provider-specific types."""
        ...

    def put(self, collection: str, key: str, value: Any) -> StorageResult:
        """Store one value without exposing provider-specific types."""
        ...

    def delete(self, collection: str, key: str) -> StorageResult:
        """Delete one value without exposing provider-specific types."""
        ...
