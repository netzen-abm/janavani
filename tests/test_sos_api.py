import base64
import hashlib
import hmac
import json
import os
import time

from fastapi.testclient import TestClient

from src.web.canonical_app import app

SECRET = "test-identity-secret"
client = TestClient(app)


def setup_function() -> None:
    os.environ["JANAVANI_IDENTITY_ASSERTION_SECRET"] = SECRET


def _auth_header(principal_id: str = "principal-1") -> dict[str, str]:
    now = int(time.time())
    payload = {
        "iss": "janavani-identity",
        "aud": "janavani-api",
        "sub": principal_id,
        "provider": "test-identity",
        "subject": principal_id,
        "principal_id": principal_id,
        "authentication_method": "passkey",
        "iat": now,
        "exp": now + 60,
        "jti": f"test-{principal_id}-{now}",
        "capabilities": ["sos:trigger"],
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    signature = hmac.new(SECRET.encode(), encoded.encode(), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    return {"Authorization": f"Bearer {encoded}.{signed}"}


def test_sos_requires_authenticated_identity() -> None:
    response = client.post(
        "/api/v1/sos/trigger",
        json={"incident_context": "harassment", "explicit_user_choice": True},
    )
    assert response.status_code == 401


def test_sos_requires_explicit_user_choice() -> None:
    response = client.post(
        "/api/v1/sos/trigger",
        headers=_auth_header(),
        json={"incident_context": "harassment"},
    )
    assert response.status_code == 403


def test_remote_sos_requires_idempotency_key() -> None:
    response = client.post(
        "/api/v1/sos/trigger",
        headers=_auth_header(),
        json={
            "incident_context": "harassment",
            "destination_refs": ["control-room-ref"],
            "explicit_user_choice": True,
            "remote_transmission": True,
        },
    )
    assert response.status_code == 422


def test_local_sos_is_truthfully_local_only() -> None:
    response = client.post(
        "/api/v1/sos/trigger",
        headers=_auth_header(),
        json={"incident_context": "harassment", "explicit_user_choice": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "LOCAL_ONLY"
    assert body["deliveries"] == []
    assert body["submission"] == "not_submitted"
    assert body["police_delivery"] == "not_implemented"
