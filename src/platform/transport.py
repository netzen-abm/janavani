"""Canonical channel-neutral transport boundary.

Transport adapters translate provider-native events into capability requests and
capability results into provider-native outbound messages. They do not own
business logic, storage, AI policy, or document generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class TransportMessage:
    """Normalized inbound or outbound transport message."""

    transport: str
    message_id: str
    conversation_id: str | None = None
    actor_ref: str | None = None
    text: str | None = None
    attachments: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransportResult:
    """Truthful transport outcome; acceptance is not delivery acknowledgement."""

    status: str
    message_id: str | None = None
    provider_reference: str | None = None
    error_code: str | None = None
    retryable: bool = False


class TransportAdapter(Protocol):
    """Replaceable adapter for one transport/provider family."""

    name: str

    def health(self) -> Mapping[str, Any]:
        """Return non-sensitive transport health/configuration state."""
        ...

    def receive(self, native_event: Any) -> TransportMessage | None:
        """Normalize one provider-native inbound event."""
        ...

    def send(self, message: TransportMessage) -> TransportResult:
        """Attempt delivery and report the actual transport state."""
        ...
