"""Redis implementation of the shared aggregate analytics boundary."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import redis

from src.platform.analytics import AnalyticsResult


class RedisAnalyticsAdapter:
    """Provider adapter for privacy-preserving aggregate counters."""

    name = "redis"

    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    @classmethod
    def from_env(cls) -> "RedisAnalyticsAdapter":
        return cls(
            redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                decode_responses=True,
            )
        )

    def increment(self, metric: str, dimensions: dict[str, str] | None = None) -> AnalyticsResult:
        if not metric.strip():
            return AnalyticsResult(ok=False, error_code="INVALID_METRIC")
        # Dimensions are deliberately limited to caller-supplied aggregate labels;
        # no actor, IP, request, or other identifying dimensions are introduced here.
        labels = dimensions or {}
        suffix = ":".join(f"{k}={v}" for k, v in sorted(labels.items()))
        key = f"metrics:aggregate:{metric}" + (f":{suffix}" if suffix else "")
        try:
            value = self._client.incr(key)
            return AnalyticsResult(ok=True, value=value)
        except redis.RedisError as exc:
            return AnalyticsResult(ok=False, error_code=type(exc).__name__)

    def snapshot(self) -> AnalyticsResult:
        try:
            value = self._client.get("metrics:global:total_generations")
            return AnalyticsResult(
                ok=True,
                value={
                    "total_documents_generated_globally": int(value) if value else 0,
                    "timestamp_checked_utc": datetime.now(timezone.utc).isoformat(),
                },
            )
        except (redis.RedisError, TypeError, ValueError) as exc:
            return AnalyticsResult(ok=False, error_code=type(exc).__name__)
