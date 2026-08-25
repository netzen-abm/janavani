"""Redis implementation of the shared transient cache boundary."""

from __future__ import annotations

import json
import os
from typing import Any

import redis

from src.platform.cache import CacheResult


class RedisCacheAdapter:
    """Provider adapter for Janavani's transient Redis cache."""

    name = "redis"

    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    @classmethod
    def from_env(cls) -> "RedisCacheAdapter":
        return cls(
            redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                decode_responses=True,
            )
        )

    def put(self, key: str, value: Any, ttl_seconds: int) -> CacheResult:
        if not key.strip():
            return CacheResult(ok=False, error_code="INVALID_KEY")
        if ttl_seconds <= 0:
            return CacheResult(ok=False, error_code="INVALID_TTL")
        try:
            ok = self._client.setex(key, ttl_seconds, json.dumps(value))
            return CacheResult(ok=bool(ok))
        except (redis.RedisError, TypeError, ValueError) as exc:
            return CacheResult(ok=False, error_code=type(exc).__name__)

    def get(self, key: str) -> CacheResult:
        try:
            raw = self._client.get(key)
            if raw is None:
                return CacheResult(ok=True, value=None)
            return CacheResult(ok=True, value=json.loads(raw))
        except (redis.RedisError, TypeError, ValueError) as exc:
            return CacheResult(ok=False, error_code=type(exc).__name__)

    def delete(self, key: str) -> CacheResult:
        try:
            return CacheResult(ok=True, value=bool(self._client.delete(key)))
        except redis.RedisError as exc:
            return CacheResult(ok=False, error_code=type(exc).__name__)
