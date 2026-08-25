"""Stable shared contracts for independently operable Janavani surfaces.

These contracts deliberately contain no provider-specific implementation.
Future transports, storage systems, AI runtimes, Web3/Web5 integrations, and
new clients can implement the contracts without changing domain capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


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
    """Channel-neutral capability result with explicit failure/degraded state."""

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


class TransportAdapter(Protocol):
    """Contract for a client or transport adapter."""

    name: str

    def health(self) -> Mapping[str, Any]:
        ...


class StorageAdapter(Protocol):
    """Replaceable persistence/storage boundary."""

    name: str

    def health(self) -> Mapping[str, Any]:
        ...


class AIProviderAdapter(Protocol):
    """Replaceable AI provider/runtime boundary."""

    name: str

    def health(self) -> Mapping[str, Any]:
        ...
