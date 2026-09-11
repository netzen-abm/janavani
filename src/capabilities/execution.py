"""Shared boundary for creating canonical capability execution contexts."""
from __future__ import annotations

from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext


CAPABILITY_ID = "platform:execution"


class CapabilityExecutionCapability:
    """Surface-neutral factory for the ecosystem execution envelope."""

    def create(
        self,
        identity: IdentityContext,
        *,
        capability_id: str,
        action: str,
        surface: str,
        **kwargs: object,
    ) -> CapabilityExecutionContext:
        return CapabilityExecutionContext.for_capability(
            identity,
            capability_id=capability_id,
            action=action,
            surface=surface,
            **kwargs,
        )
