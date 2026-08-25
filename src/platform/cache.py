"""Provider-neutral transient cache capability contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class CacheResult:
    """Channel-neutral result for transient cache operations."""

    ok: bool
    value: Any = None
    error_code: str | None = None


class CacheAdapter(Protocol):
    """Replaceable transient-cache provider boundary."""

    def put(self, key: str, value: Any, ttl_seconds: int) -> CacheResult:
        ...

    def get(self, key: str) -> CacheResult:
        ...

    def delete(self, key: str) -> CacheResult:
        ...
