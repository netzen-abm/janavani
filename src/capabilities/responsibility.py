"""Shared application boundary for responsibility resolution."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.responsibility import (
    ResponsibilityObservation,
    ResponsibilityResolution,
    ResponsibilityResolver,
)


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
        self, request: ResponsibilityResolutionRequest
    ) -> ResponsibilityResolution:
        resolution = self._resolver.resolve(request.observation)
        resolution.require_source()
        return resolution
