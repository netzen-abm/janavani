"""Legacy transient cache implementation kept for migration compatibility.

New code should use the provider-neutral cache contract and adapter. This module
remains temporarily isolated while existing consumers are traced and migrated.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import redis

logger = logging.getLogger("janavani.storage.cache")


class TransientStorageEngine:
    """Redis-backed transient document cache with a bounded TTL."""

    def __init__(self, ttl_seconds: int = 1800) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True,
        )
        self.expiry_ttl_seconds = ttl_seconds

    def cache_transient_document(self, task_id: str, document_payload: dict[str, Any]) -> bool:
        """Store a transient payload with automatic expiration."""
        try:
            serialized_data = json.dumps(document_payload)
            return bool(
                self.redis_client.setex(
                    name=f"transient_doc:{task_id}",
                    time=self.expiry_ttl_seconds,
                    value=serialized_data,
                )
            )
        except (redis.RedisError, TypeError, ValueError) as exc:
            logger.warning("Transient cache write failed: %s", type(exc).__name__)
            return False

    def retrieve_transient_document(self, task_id: str) -> dict[str, Any] | None:
        """Retrieve a transient payload if it has not expired."""
        try:
            raw_data = self.redis_client.get(f"transient_doc:{task_id}")
            if raw_data is None:
                return None
            value = json.loads(raw_data)
            return value if isinstance(value, dict) else None
        except (redis.RedisError, TypeError, ValueError):
            return None
