"""Shared verification functions for Meta webhook ingress."""
import hashlib
import hmac
from typing import Optional


def verify_meta_webhook_challenge(
    mode: Optional[str],
    supplied_token: Optional[str],
    challenge: Optional[str],
    expected_token: Optional[str],
) -> tuple[str, int]:
    """Validate Meta's subscription handshake using the configured verify token."""
    if not expected_token or mode != "subscribe" or not supplied_token or not challenge:
        return "", 403
    if not hmac.compare_digest(supplied_token, expected_token):
        return "", 403
    return challenge, 200


def is_valid_meta_signature(
    raw_body: bytes,
    signature_header: Optional[str],
    app_secret: Optional[str],
) -> bool:
    """Validate X-Hub-Signature-256 over the raw request bytes."""
    if not app_secret or not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        app_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature_header, expected)
