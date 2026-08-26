"""Stable shared capability contracts for independently operable surfaces.

Provider- and transport-specific contracts live in their dedicated modules:
``transport.py`` and ``storage.py``. This module owns the channel-neutral
request/result and capability-handler contracts and re-exports those adapter
protocols for compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from .storage import StorageAdapter
from .transport import TransportAdapter


@dataclass(frozen=True)
class CapabilityRequest:
    """Normalized request crossing an interface into a shared capability."""

    capability: str
    request_id: str
    actor_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilityResult:
    """Channel-neutral capability result with explicit outcome state."""

    capability: str
    request_id: str
    status: str
    data: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    error_code: str | None = None


class CapabilityHandler(Protocol):
    """Implementation contract for a shared Janavani capability."""

    capability: str

    def handle(self, request: CapabilityRequest) -> CapabilityResult:
        ...


class AIProviderAdapter(Protocol):
    """Replaceable AI provider/runtime boundary."""

    name: str

    def health(self) -> Mapping[str, Any]:
        ...


__all__ = [
    "AIProviderAdapter",
    "CapabilityHandler",
    "CapabilityRequest",
    "CapabilityResult",
    "StorageAdapter",
    "TransportAdapter",
]
