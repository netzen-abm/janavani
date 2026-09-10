"""Reference responsibility resolver for tests and local development."""
from __future__ import annotations

from src.core.responsibility import (
    ResponsibilityObservation,
    ResponsibilityResolution,
)


class InMemoryResponsibilityResolver:
    """Return pre-registered resolutions without adding inference authority."""

    def __init__(self, resolutions: list[ResponsibilityResolution] | None = None) -> None:
        self._resolutions = {
            resolution.observation_id: resolution
            for resolution in resolutions or []
        }

    def save(self, resolution: ResponsibilityResolution) -> None:
        self._resolutions[resolution.observation_id] = resolution

    def resolve(self, observation: ResponsibilityObservation) -> ResponsibilityResolution:
        try:
            return self._resolutions[observation.observation_id]
        except KeyError as exc:
            raise LookupError("Responsibility resolution not found") from exc
