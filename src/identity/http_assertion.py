"""Verified HTTP identity assertion boundary.

This module does not authenticate citizens with a provider. It verifies a
short-lived assertion produced by a trusted Janavani identity gateway or
future OIDC/passkey gateway, then converts the verified identity into the
canonical IdentityContext.

An arbitrary actor/principal supplied by a browser is never trusted.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Iterable

from fastapi import Header, HTTPException

from .adapter import DefaultIdentityAdapter
from .context import IdentityContext
from .external import ExternalIdentity


@dataclass(frozen=True)
class IdentityAssertionVerifier:
    secret: bytes
    expected_issuer: str | None = None
    expected_audience: str | None = None
    max_clock_skew_seconds: int = 30
    max_lifetime_seconds: int = 300

    def verify(self, assertion: str) -> ExternalIdentity:
        try:
            encoded_payload, encoded_signature = assertion.split(".", 1)
            payload_bytes = _b64decode(encoded_payload)
            supplied_signature = _b64decode(encoded_signature)
            expected_signature = hmac.new(
                self.secret,
                encoded_payload.encode("ascii"),
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(supplied_signature, expected_signature):
                raise ValueError("invalid identity assertion signature")
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
            raise ValueError("invalid identity assertion") from exc

        required = ("principal_id", "provider", "subject", "authentication_method", "iat", "exp", "jti")
        if any(not payload.get(key) for key in required):
            raise ValueError("identity assertion is missing required fields")

        if not isinstance(payload["principal_id"], str) or not payload["principal_id"]:
            raise ValueError("principal_id must be opaque text")

        try:
            issued_at = int(payload["iat"])
            expires_at = int(payload["exp"])
        except (TypeError, ValueError) as exc:
            raise ValueError("identity assertion lifetime is invalid") from exc

        now = int(time.time())
        if issued_at > now + self.max_clock_skew_seconds:
            raise ValueError("identity assertion is issued in the future")
        if expires_at < now - self.max_clock_skew_seconds:
            raise ValueError("identity assertion has expired")
        if expires_at <= issued_at or expires_at - issued_at > self.max_lifetime_seconds:
            raise ValueError("identity assertion lifetime is invalid")

        if self.expected_issuer is not None and payload.get("iss") != self.expected_issuer:
            raise ValueError("identity assertion issuer is invalid")
        if self.expected_audience is not None and payload.get("aud") != self.expected_audience:
            raise ValueError("identity assertion audience is invalid")

        return ExternalIdentity(
            provider=str(payload["provider"]),
            subject=str(payload["subject"]),
            principal_id=payload["principal_id"],
            authentication_method=str(payload["authentication_method"]),
            verified=True,
            scopes=frozenset(_string_values(payload.get("scopes", []))),
            capabilities=frozenset(_string_values(payload.get("capabilities", []))),
        )


def require_authenticated_identity(
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> IdentityContext:
    """Resolve a verified identity assertion into the canonical request context."""
    secret_value = os.getenv("JANAVANI_IDENTITY_ASSERTION_SECRET", "").strip()
    if not secret_value:
        raise HTTPException(
            status_code=503,
            detail="Authenticated identity gateway is not configured",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authenticated identity required")

    assertion = authorization.removeprefix("Bearer ").strip()
    try:
        verifier = IdentityAssertionVerifier(
            secret=secret_value.encode("utf-8"),
            expected_issuer=os.getenv("JANAVANI_IDENTITY_ASSERTION_ISSUER") or None,
            expected_audience=os.getenv("JANAVANI_IDENTITY_ASSERTION_AUDIENCE") or None,
        )
        identity = verifier.verify(assertion)
        context = DefaultIdentityAdapter().resolve(identity)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authenticated identity") from exc

    return IdentityContext(principal=context.principal, request_id=request_id)


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _string_values(values: Iterable[object]) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise ValueError("identity assertion collections must be arrays")
    try:
        return [value for value in values if isinstance(value, str) and value]
    except TypeError as exc:
        raise ValueError("identity assertion collections must be arrays") from exc
