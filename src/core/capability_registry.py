"""Canonical registry for Janavani shared capabilities.

The registry is metadata, not business logic. It makes the shared-infrastructure
assessment executable and gives every access surface one authoritative capability
catalog to discover available functionality and its policy requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Mapping


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    name: str
    description: str
    consumers: FrozenSet[str]
    requires_ai: bool = False
    ai_user_controlled: bool = True
    consent_required: bool = False
    consequential: bool = False
    output_formats: FrozenSet[str] = frozenset()
    required_data_classes: FrozenSet[str] = frozenset()
    provider_independent: bool = True
    deterministic_fallback: bool = True
    status: str = "planned"
    metadata: Mapping[str, str] = field(default_factory=dict)


class CapabilityRegistry:
    """Single catalog of reusable Janavani capabilities."""

    def __init__(self, descriptors: tuple[CapabilityDescriptor, ...] = ()):
        self._items: dict[str, CapabilityDescriptor] = {}
        for descriptor in descriptors:
            self.register(descriptor)

    def register(self, descriptor: CapabilityDescriptor) -> None:
        if not descriptor.capability_id.strip():
            raise ValueError("capability_id is required")
        if descriptor.capability_id in self._items:
            raise ValueError(f"Capability already registered: {descriptor.capability_id}")
        if not descriptor.consumers:
            raise ValueError("A shared capability must declare at least one consumer")
        if descriptor.requires_ai and not descriptor.ai_user_controlled:
            raise ValueError("AI capability must remain user-controlled")
        self._items[descriptor.capability_id] = descriptor

    def get(self, capability_id: str) -> CapabilityDescriptor:
        return self._items[capability_id]

    def all(self) -> tuple[CapabilityDescriptor, ...]:
        return tuple(self._items.values())

    def for_consumer(self, consumer: str) -> tuple[CapabilityDescriptor, ...]:
        return tuple(item for item in self._items.values() if consumer in item.consumers)

    def ids(self) -> frozenset[str]:
        return frozenset(self._items)


DEFAULT_CAPABILITIES = (
    CapabilityDescriptor(
        "case",
        "Case",
        "Create and manage a citizen civic issue case.",
        frozenset({"webapp", "telegram", "telegram_miniapp", "mobile", "dapp"}),
        required_data_classes=frozenset({"public", "non_sensitive", "personal", "sensitive"}),
        status="in_progress",
    ),
    CapabilityDescriptor(
        "authority.discovery",
        "Authority Discovery",
        "Identify the responsible civic authority from the issue and jurisdiction.",
        frozenset({"webapp", "telegram", "telegram_miniapp", "mobile", "dapp"}),
        status="in_progress",
    ),
    CapabilityDescriptor(
        "evidence",
        "Evidence",
        "Capture and manage citizen evidence with local-first privacy.",
        frozenset({"webapp", "telegram", "telegram_miniapp", "mobile", "dapp"}),
        required_data_classes=frozenset({"personal", "sensitive"}),
        status="in_progress",
    ),
    CapabilityDescriptor(
        "document",
        "Document",
        "Compose and render civic documents from a shared structured model.",
        frozenset({"webapp", "telegram", "telegram_miniapp", "mobile", "dapp"}),
        output_formats=frozenset({"pdf", "document"}),
        status="in_progress",
    ),
    CapabilityDescriptor(
        "ai",
        "AI Assistance",
        "Provide AI assistance using sanitized context when the citizen chooses AI.",
        frozenset({"webapp", "telegram", "telegram_miniapp", "mobile", "dapp"}),
        requires_ai=True,
        ai_user_controlled=True,
        status="in_progress",
    ),
    CapabilityDescriptor(
        "agentic_ai",
        "Agentic AI",
        "Perform scoped reasoning and tool operations under consent and confirmation policy.",
        frozenset({"webapp", "telegram", "telegram_miniapp", "mobile", "dapp"}),
        requires_ai=True,
        ai_user_controlled=True,
        consent_required=True,
        consequential=True,
        status="in_progress",
    ),
)


def default_registry() -> CapabilityRegistry:
    return CapabilityRegistry(DEFAULT_CAPABILITIES)
