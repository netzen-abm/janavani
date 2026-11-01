"""Shared, atomic replay protection for short-lived identity assertions.

The Redis key stores only a digest-derived assertion identifier, never the
signed assertion, principal, or raw jti. Production callers must fail closed
when this store cannot be used.
"""
from __future__ import annotations

import hashlib
import time
from typing import Protocol

import redis


class ReplayProtectionUnavailable(RuntimeError):
    """Raised when replay protection cannot safely decide an assertion."""


class IdentityAssertionReplayStore(Protocol):
    """Atomic single-use claim contract for verified assertion identifiers."""

    def consume(self, assertion_id: str, expires_at: int) -> bool:
        """Claim an identifier once, retaining it no later than expires_at."""


class RedisIdentityAssertionReplayStore:
    """Redis-backed cross-process replay protection using atomic SET NX EX."""

    _PREFIX = "janavani:identity-assertion-replay:v1:"

    def __init__(self, redis_url: str) -> None:
        if not redis_url or not redis_url.strip():
            raise ValueError("identity replay Redis URL is required")
        self._client = redis.Redis.from_url(
            redis_url.strip(),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=False,
        )

    def consume(self, assertion_id: str, expires_at: int) -> bool:
        # Floor the remaining duration so Redis expiry cannot extend beyond
        # the assertion's absolute expiry because of fractional clock seconds.
        remaining = int(int(expires_at) - time.time())
        if remaining <= 0:
            return False

        # Hash again at the persistence boundary so callers cannot cause raw
        # assertion identifiers to appear in Redis key names or diagnostics.
        digest = hashlib.sha256(assertion_id.encode("utf-8")).hexdigest()
        try:
            claimed = self._client.set(
                f"{self._PREFIX}{digest}",
                "1",
                nx=True,
                ex=remaining,
            )
        except redis.RedisError as exc:
            raise ReplayProtectionUnavailable(
                "identity assertion replay protection is unavailable"
            ) from exc
        return bool(claimed)
