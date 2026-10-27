"""Tests for Meta webhook handshake and signature verification."""
import hashlib
import hmac

from src.adapters.meta_webhook_security import (
    is_valid_meta_signature,
    verify_meta_webhook_challenge,
)


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
    secret = "test-app-secret"
    signature = "sha256=" + hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()

    assert is_valid_meta_signature(body, signature, secret)
    assert not is_valid_meta_signature(body + b" ", signature, secret)
    assert not is_valid_meta_signature(body, signature, None)
    assert not is_valid_meta_signature(body, "sha256=bad", secret)
