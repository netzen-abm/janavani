"""Shared application boundary for obligation resolution."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.obligation import (
    ObligationObservation,
    ObligationResolution,
    ObligationResolver,
)


CAPABILITY_ID = "obligation:resolve"


@dataclass(frozen=True)
class ObligationResolutionRequest:
    """Surface-neutral request for resolving applicable obligations."""

    observation: ObligationObservation


class ObligationCapability:
    """Canonical application boundary; providers cannot become legal authority."""

    def __init__(self, resolver: ObligationResolver) -> None:
        self._resolver = resolver

    def resolve(
        self, request: ObligationResolutionRequest
    ) -> ObligationResolution:
        resolution = self._resolver.resolve(request.observation)
        resolution.require_source()
        return resolution
