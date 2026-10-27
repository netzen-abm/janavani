"""Tests for environment-driven Redis client construction."""
from unittest.mock import patch

from src.storage.redis_connection import create_redis_client


def test_create_redis_client_uses_configured_environment(monkeypatch):
    monkeypatch.setenv("REDIS_HOST", "redis.test.internal")
    monkeypatch.setenv("REDIS_PORT", "6381")

    with patch("src.storage.redis_connection.redis.Redis") as constructor:
        client = create_redis_client()

    constructor.assert_called_once_with(
        host="redis.test.internal",
        port=6381,
        db=0,
        decode_responses=True,
    )
    assert client is constructor.return_value


def test_create_redis_client_has_safe_local_defaults(monkeypatch):
    monkeypatch.delenv("REDIS_HOST", raising=False)
    monkeypatch.delenv("REDIS_PORT", raising=False)

    with patch("src.storage.redis_connection.redis.Redis") as constructor:
        create_redis_client()

    constructor.assert_called_once_with(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )
