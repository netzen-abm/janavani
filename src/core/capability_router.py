"""Single routing boundary for all Janavani access surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from core.contracts.access_surface import CapabilityHandler, CapabilityRequest, CapabilityResponse


@dataclass
class CapabilityRouter:
    """Routes normalized requests to registered shared capabilities."""

    handlers: Dict[str, CapabilityHandler]

    def __init__(self):
        self.handlers = {}

    def register(self, capability_id: str, handler: CapabilityHandler) -> None:
        key = capability_id.strip().lower()
        if not key:
            raise ValueError("capability_id is required")
        if key in self.handlers:
            raise ValueError(f"Capability already registered: {capability_id}")
        self.handlers[key] = handler

    def dispatch(self, request: CapabilityRequest) -> CapabilityResponse:
        handler = self.handlers.get(request.capability_id.strip().lower())
        if handler is None:
            return CapabilityResponse(
                request_id=request.request_id,
                ok=False,
                status="rejected",
                error_code="unknown_capability",
            )
        return handler.handle(request)
