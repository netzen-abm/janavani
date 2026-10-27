"""Tests for Meta webhook challenge verification and signed delivery."""
import hashlib
import hmac
import json

from flask import Flask

from src.adapters.meta_webhook_security import (
    is_valid_meta_signature,
    register_meta_webhook_routes,
    verify_meta_webhook_challenge,
)


def signed_body(body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_challenge_requires_configured_matching_token():
    assert verify_meta_webhook_challenge(
        "subscribe", "verify-me", "challenge-1", "verify-me"
    ) == ("challenge-1", 200)
    assert verify_meta_webhook_challenge(
        "subscribe", "wrong-token", "challenge-1", "verify-me"
    ) == ("", 403)
    assert verify_meta_webhook_challenge(
        "subscribe", "verify-me", "challenge-1", None
    ) == ("", 403)


def test_signature_requires_exact_raw_body_hmac():
    body = b'{"object":"whatsapp_business_account"}'
    signature = signed_body(body, "test-app-secret")
    assert is_valid_meta_signature(body, signature, "test-app-secret")
    assert not is_valid_meta_signature(body + b" ", signature, "test-app-secret")
    assert not is_valid_meta_signature(body, signature, None)
    assert not is_valid_meta_signature(body, "sha256=bad", "test-app-secret")


def test_registered_route_rejects_bad_signature_and_retries_without_dispatch():
    app = Flask("meta-webhook-test")
    register_meta_webhook_routes(
        app, channel="test", verify_token="verify", app_secret="secret"
    )
    client = app.test_client()
    body = json.dumps({"object": "page"}).encode("utf-8")

    rejected = client.post(
        "/webhook", data=body, content_type="application/json",
        headers={"X-Hub-Signature-256": "sha256=bad"},
    )
    assert rejected.status_code == 401

    valid_but_unhandled = client.post(
        "/webhook", data=body, content_type="application/json",
        headers={"X-Hub-Signature-256": signed_body(body, "secret")},
    )
    assert valid_but_unhandled.status_code == 503
    assert valid_but_unhandled.json == {"error": "event_dispatch_unavailable"}


def test_registered_route_acks_only_after_dispatcher_accepts_event():
    received = []
    app = Flask("meta-webhook-dispatch-test")
    register_meta_webhook_routes(
        app,
        channel="test",
        verify_token="verify",
        app_secret="secret",
        event_dispatcher=lambda payload: received.append(payload) is None,
    )
    client = app.test_client()
    body = b'{"object":"page"}'

    response = client.post(
        "/webhook", data=body, content_type="application/json",
        headers={"X-Hub-Signature-256": signed_body(body, "secret")},
    )
    assert response.status_code == 200
    assert response.json == {"status": "accepted"}
    assert received == [{"object": "page"}]


def test_registered_route_verifies_token_and_challenge():
    app = Flask("meta-webhook-challenge-test")
    register_meta_webhook_routes(
        app, channel="test", verify_token="verify", app_secret="secret"
    )
    client = app.test_client()

    good = client.get(
        "/webhook?hub.mode=subscribe&hub.verify_token=verify&hub.challenge=challenge"
    )
    bad = client.get(
        "/webhook?hub.mode=subscribe&hub.verify_token=bad&hub.challenge=challenge"
    )
    assert good.status_code == 200
    assert good.get_data(as_text=True) == "challenge"
    assert bad.status_code == 403
