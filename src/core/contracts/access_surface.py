"""Channel-neutral request/response contracts for Janavani access surfaces.

Telegram, WebApp, Mini App and future clients must translate their native input
into these contracts instead of implementing capability business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class CapabilityRequest:
    request_id: str
    capability_id: str
    action: str
    input: Mapping[str, Any] = field(default_factory=dict)
    language: str = "en"
    source: str = "unknown"
    user_choice: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CapabilityResponse:
    request_id: str
    ok: bool
    status: str
    data: Mapping[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    next_action: Optional[str] = None


class CapabilityHandler:
    """Minimal protocol implemented by shared capabilities."""

    def handle(self, request: CapabilityRequest) -> CapabilityResponse:
        raise NotImplementedError
