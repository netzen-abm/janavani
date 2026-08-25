"""Small runtime registry for shared capabilities and adapters."""

from __future__ import annotations

from typing import Any

from platform.contracts import CapabilityHandler


class CapabilityRegistry:
    """Resolve capability implementations without coupling clients to them."""

    def __init__(self) -> None:
        self._handlers: dict[str, CapabilityHandler] = {}

    def register(self, handler: CapabilityHandler) -> None:
        name = handler.capability.strip().lower()
        if not name:
            raise ValueError("capability name must not be empty")
        self._handlers[name] = handler

    def get(self, capability: str) -> CapabilityHandler:
        name = capability.strip().lower()
        try:
            return self._handlers[name]
        except KeyError as exc:
            raise LookupError(f"Capability is not registered: {capability}") from exc

    def has(self, capability: str) -> bool:
        return capability.strip().lower() in self._handlers

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))
