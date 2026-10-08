from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from src.adapters.telegram.identity import identity_for_telegram_user
from src.identity.external import ExternalIdentity
from src.identity.http_assertion import IdentityAssertionVerifier
from src.identity.linking import InMemoryExternalIdentityLinkRepository


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _assertion(secret: bytes, principal_id: str) -> str:
    now = int(time.time())
    payload = {
        "principal_id": principal_id,
        "provider": "web-identity-gateway",
        "subject": "web-subject-001",
        "authentication_method": "oidc",
        "iat": now,
        "exp": now + 120,
        "jti": "parity-jti-001",
    }
    encoded = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
    return encoded + "." + _b64(signature)


def test_web_assertion_and_telegram_link_converge_on_same_principal():
    principal_id = "janavani:parity-principal"

    links = InMemoryExternalIdentityLinkRepository()
    links.save(
        ExternalIdentity(
            provider="telegram",
            subject="12345",
            principal_id=principal_id,
            authentication_method="explicit_verified_link",
            verified=True,
        )
    )

    telegram_identity = identity_for_telegram_user(
        12345, links=links
    )

    secret = b"test-parity-secret"
    web_identity = IdentityAssertionVerifier(secret=secret).verify(
        _assertion(secret, principal_id)
    )

    assert telegram_identity.principal.principal_id == principal_id
    assert web_identity.principal_id == principal_id
    assert telegram_identity.principal.principal_id == web_identity.principal_id
