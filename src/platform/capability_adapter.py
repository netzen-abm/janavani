"""Bridge transport messages to shared capability contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import CapabilityRequest, CapabilityResult
from .registry import CapabilityRegistry
from .transport import TransportMessage


@dataclass(frozen=True)
class CapabilityDispatchResult:
    """Outcome of translating and dispatching one transport message."""

    capability: str
    result: CapabilityResult


def dispatch_transport_message(
    message: TransportMessage,
    registry: CapabilityRegistry,
    capability: str,
    payload: dict[str, Any] | None = None,
) -> CapabilityDispatchResult:
    """Dispatch a normalized transport message without coupling the transport to a capability."""
    request = CapabilityRequest(
        capability=capability,
        actor_ref=message.actor_ref,
        channel=message.transport,
        payload={
            "message_id": message.message_id,
            "conversation_id": message.conversation_id,
            "text": message.text,
            "attachments": list(message.attachments),
            **(payload or {}),
        },
    )
    handler = registry.get(capability)
    result = handler.handle(request)
    return CapabilityDispatchResult(capability=capability, result=result)
