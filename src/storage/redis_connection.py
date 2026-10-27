"""Shared Redis connection configuration.

This module creates clients only; callers retain their own error handling and
business semantics. Connection details come from environment variables.
"""
import os

import redis


def create_redis_client() -> redis.Redis:
    """Create a Redis client with the ecosystem's common runtime settings."""
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
    )
