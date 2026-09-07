import base64
import hashlib
import hmac
import json
import time

import pytest

from src.identity.http_assertion import IdentityAssertionVerifier


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
