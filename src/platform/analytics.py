"""Provider-neutral aggregate analytics contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class AnalyticsResult:
    """Channel-neutral result for aggregate telemetry operations."""

    ok: bool
    value: Any = None
    error_code: str | None = None


class AnalyticsAdapter(Protocol):
    """Replaceable aggregate-telemetry provider boundary."""

    def increment(self, metric: str, dimensions: dict[str, str] | None = None) -> AnalyticsResult:
        ...

    def snapshot(self) -> AnalyticsResult:
        ...
