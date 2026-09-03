"""Shared bounded abuse control for anonymous capability calls.

This is deliberately provider-neutral and process-local. Production deployments
should place a distributed rate-limit implementation behind the same contract.
"""

from dataclasses import dataclass
from threading import RLock
import time


class AbuseLimitExceeded(PermissionError):
    """Raised when a principal exceeds a capability's request budget."""


@dataclass(frozen=True)
class RateLimit:
    max_requests: int
    window_seconds: int


class AbuseController:
    def __init__(self):
        self._events: dict[tuple[str, str], list[float]] = {}
        self._lock = RLock()

    def check(self, principal_id: str, capability: str, limit: RateLimit) -> None:
        now = time.monotonic()
        key = (principal_id, capability)
        cutoff = now - limit.window_seconds
        with self._lock:
            events = [event for event in self._events.get(key, []) if event > cutoff]
            if len(events) >= limit.max_requests:
                self._events[key] = events
                raise AbuseLimitExceeded("request rate limit exceeded")
            events.append(now)
            self._events[key] = events


DEFAULT_ANONYMOUS_LIMIT = RateLimit(max_requests=30, window_seconds=60)
