"""Shared application boundary for responsibility resolution."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.execution import CapabilityExecutionContext
from src.core.responsibility import (
    ResponsibilityObservation,
    ResponsibilityResolution,
    ResponsibilityResolver,
)
from src.identity.context import IdentityContext


CAPABILITY_ID = "responsibility:resolve"


@dataclass(frozen=True)
class ResponsibilityResolutionRequest:
    """Surface-neutral request for resolving responsibility candidates."""

    observation: ResponsibilityObservation


class ResponsibilityCapability:
    """Canonical application boundary; providers cannot become domain authority."""

    def __init__(self, resolver: ResponsibilityResolver) -> None:
        self._resolver = resolver

    def resolve(
        self,
        request: ResponsibilityResolutionRequest,
        *,
        identity: IdentityContext | None = None,
        execution_context: CapabilityExecutionContext | None = None,
    ) -> ResponsibilityResolution:
        if execution_context is not None:
            if identity is None:
                raise ValueError("Identity is required when execution_context is supplied")
            if execution_context.identity.principal.principal_id != identity.principal.principal_id:
                raise PermissionError("Execution identity does not match the authenticated identity")
            if execution_context.capability_id != CAPABILITY_ID:
                raise ValueError("Execution capability does not match the Responsibility capability")
            if execution_context.action != "responsibility:resolve":
                raise ValueError("Execution action does not match the Responsibility operation")
        resolution = self._resolver.resolve(request.observation)
        resolution.require_source()
        return resolution
