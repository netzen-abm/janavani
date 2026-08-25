"""Provider-neutral aggregate analytics capability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


# Only non-identifying aggregate dimensions are permitted at the capability
# boundary. Providers and callers must not use this API for user tracking.
ALLOWED_DIMENSIONS = frozenset({"document_type", "status", "capability", "channel_type"})
FORBIDDEN_DIMENSION_TERMS = frozenset(
    {"user", "actor", "email", "phone", "ip", "device", "session", "tracking", "request", "identity"}
)


@dataclass(frozen=True)
class AnalyticsResult:
    """Channel-neutral result for aggregate telemetry operations."""

    ok: bool
    value: Any = None
    error_code: str | None = None


class AnalyticsAdapter(Protocol):
    """Replaceable aggregate-telemetry provider boundary."""

    name: str

    def increment(self, metric: str, dimensions: dict[str, str] | None = None) -> AnalyticsResult: ...

    def snapshot(self) -> AnalyticsResult: ...


def validate_dimensions(dimensions: dict[str, str] | None) -> AnalyticsResult:
    """Reject dimensions that could turn aggregate telemetry into tracking."""
    for key in dimensions or {}:
        normalized = key.strip().lower()
        if normalized not in ALLOWED_DIMENSIONS:
            return AnalyticsResult(ok=False, error_code="DIMENSION_NOT_ALLOWED")
        if any(term in normalized for term in FORBIDDEN_DIMENSION_TERMS):
            return AnalyticsResult(ok=False, error_code="IDENTIFYING_DIMENSION_FORBIDDEN")
    return AnalyticsResult(ok=True)
