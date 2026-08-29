"""Runtime capability registry and provider plug-in boundary.

Optional means user-selectable, never platform-omitted. Providers can be added
without changing WebApp code; clients discover capabilities through this registry.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class CapabilityDescriptor:
    key: str
    version: str
    title: str
    user_optional: bool = True
    provider: str = "platform"
    status: str = "available"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityRegistry:
    _descriptors: dict[str, CapabilityDescriptor] = field(default_factory=dict)
    _providers: dict[str, Callable[[], Any]] = field(default_factory=dict)

    def register(self, descriptor: CapabilityDescriptor, provider_factory: Callable[[], Any] | None = None) -> None:
        self._descriptors[descriptor.key] = descriptor
        if provider_factory:
            self._providers[descriptor.key] = provider_factory

    def list(self) -> list[CapabilityDescriptor]:
        return list(self._descriptors.values())

    def get(self, key: str) -> CapabilityDescriptor | None:
        return self._descriptors.get(key)

    def resolve(self, key: str) -> Any:
        factory = self._providers.get(key)
        if factory is None:
            raise KeyError(f"Capability provider unavailable: {key}")
        return factory()

    def health(self) -> dict[str, str]:
        return {key: descriptor.status for key, descriptor in self._descriptors.items()}


registry = CapabilityRegistry()

for descriptor in (
    CapabilityDescriptor("case", "1.0", "Civic Case", user_optional=False),
    CapabilityDescriptor("authority", "1.0", "Authority Intelligence"),
    CapabilityDescriptor("evidence", "1.0", "Evidence & Provenance"),
    CapabilityDescriptor("documents", "1.0", "Document Composition"),
    CapabilityDescriptor("submission", "1.0", "Civic Submission"),
    CapabilityDescriptor("tracking", "1.0", "Case Tracking"),
    CapabilityDescriptor("ai", "1.0", "AI Assistance"),
    CapabilityDescriptor("decentralized", "1.0", "Decentralized Infrastructure"),
):
    registry.register(descriptor)
