import base64
import hashlib
import hmac
import json
import threading
import time

import fakeredis
import pytest
from fastapi import HTTPException

from src.identity.http_assertion import (
    IdentityAssertionVerifier,
    ReplayProtectionUnavailable,
    require_authenticated_identity,
)
from src.identity.replay_store import RedisIdentityAssertionReplayStore


def _encode(payload: dict[str, object], secret: bytes) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{encoded}.{signed}"


def _payload(**overrides: object) -> dict[str, object]:
    now = int(time.time())
    payload: dict[str, object] = {
        "iss": "janavani-identity",
        "aud": "janavani-api",
        "sub": "provider-subject",
        "provider": "test-identity",
        "subject": "provider-subject",
        "principal_id": "principal-1",
        "authentication_method": "passkey",
        "iat": now,
        "exp": now + 60,
        "jti": "assertion-1",
        "scopes": ["case:read"],
        "capabilities": ["case:read", "case:write"],
    }
    payload.update(overrides)
    return payload


class InMemoryReplayStore:
    """Thread-safe test double; never use for multi-process production."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._claims: set[str] = set()
        self.fail = False

    def consume(self, assertion_id: str, expires_at: int) -> bool:
        if self.fail:
            raise ReplayProtectionUnavailable("replay store unavailable")
        with self._lock:
            if assertion_id in self._claims:
                return False
            self._claims.add(assertion_id)
            return True


def test_verifier_accepts_signed_short_lived_identity() -> None:
    secret = b"test-secret"
    identity = IdentityAssertionVerifier(
        secret=secret,
        expected_issuer="janavani-identity",
        expected_audience="janavani-api",
    ).verify(_encode(_payload(), secret))

    assert identity.verified is True
    assert identity.principal_id == "principal-1"
    assert "case:write" in identity.capabilities


def test_verifier_rejects_tampered_assertion() -> None:
    secret = b"test-secret"
    assertion = _encode(_payload(), secret)
    payload, signature = assertion.split(".", 1)
    tampered = f"{payload[:-1]}X.{signature}"

    with pytest.raises(ValueError, match="invalid identity assertion"):
        IdentityAssertionVerifier(secret=secret).verify(tampered)


def test_verifier_rejects_expired_assertion() -> None:
    secret = b"test-secret"
    now = int(time.time())
    assertion = _encode(_payload(iat=now - 600, exp=now - 300), secret)

    with pytest.raises(ValueError, match="expired"):
        IdentityAssertionVerifier(secret=secret).verify(assertion)


def test_verifier_rejects_wrong_audience() -> None:
    secret = b"test-secret"
    assertion = _encode(_payload(), secret)

    with pytest.raises(ValueError, match="audience"):
        IdentityAssertionVerifier(secret=secret, expected_audience="wrong-api").verify(assertion)


def test_replay_store_accepts_first_use_and_rejects_replay() -> None:
    secret = b"test-secret"
    store = InMemoryReplayStore()
    verifier = IdentityAssertionVerifier(secret=secret, replay_store=store)
    assertion = _encode(_payload(), secret)

    assert verifier.verify(assertion).principal_id == "principal-1"
    with pytest.raises(ValueError, match="replayed"):
        verifier.verify(assertion)


def test_replay_store_allows_distinct_assertion_ids() -> None:
    secret = b"test-secret"
    store = InMemoryReplayStore()
    verifier = IdentityAssertionVerifier(secret=secret, replay_store=store)

    verifier.verify(_encode(_payload(jti="assertion-1"), secret))
    verifier.verify(_encode(_payload(jti="assertion-2"), secret))


def test_concurrent_replay_attempts_have_exactly_one_success() -> None:
    secret = b"test-secret"
    store = InMemoryReplayStore()
    verifier = IdentityAssertionVerifier(secret=secret, replay_store=store)
    assertion = _encode(_payload(), secret)
    barrier = threading.Barrier(8)

    def attempt() -> bool:
        barrier.wait()
        try:
            verifier.verify(assertion)
            return True
        except ValueError:
            return False

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: attempt(), range(8)))

    assert results.count(True) == 1
    assert results.count(False) == 7


def test_replay_store_outage_fails_closed() -> None:
    secret = b"test-secret"
    store = InMemoryReplayStore()
    store.fail = True
    verifier = IdentityAssertionVerifier(secret=secret, replay_store=store)

    with pytest.raises(ReplayProtectionUnavailable):
        verifier.verify(_encode(_payload(), secret))


def test_invalid_audience_does_not_consume_assertion_id() -> None:
    secret = b"test-secret"
    store = InMemoryReplayStore()
    assertion = _encode(_payload(), secret)

    with pytest.raises(ValueError, match="audience"):
        IdentityAssertionVerifier(
            secret=secret,
            expected_audience="wrong-api",
            replay_store=store,
        ).verify(assertion)

    assert IdentityAssertionVerifier(
        secret=secret,
        expected_audience="janavani-api",
        replay_store=store,
    ).verify(assertion).verified is True



def test_redis_replay_store_is_atomic_across_instances_and_bounds_ttl() -> None:
    server = fakeredis.FakeServer()
    first = RedisIdentityAssertionReplayStore("redis://localhost/0")
    second = RedisIdentityAssertionReplayStore("redis://localhost/0")
    first._client = fakeredis.FakeRedis(server=server, decode_responses=True)
    second._client = fakeredis.FakeRedis(server=server, decode_responses=True)
    expires_at = int(time.time()) + 30

    assert first.consume("opaque-assertion-digest", expires_at) is True
    assert second.consume("opaque-assertion-digest", expires_at) is False

    keys = list(first._client.scan_iter(match="janavani:identity-assertion-replay:v1:*"))
    assert len(keys) == 1
    ttl = first._client.ttl(keys[0])
    assert 0 < ttl <= expires_at - int(time.time())



def test_authenticated_dependency_fails_closed_without_replay_store(monkeypatch) -> None:
    monkeypatch.setenv("JANAVANI_IDENTITY_ASSERTION_SECRET", "test-secret")
    monkeypatch.delenv("JANAVANI_IDENTITY_REPLAY_REDIS_URL", raising=False)

    with pytest.raises(HTTPException) as error:
        require_authenticated_identity(authorization="Bearer not-used", request_id=None)

    assert error.value.status_code == 503
