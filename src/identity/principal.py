"""Normalized identity context for all Janavani interfaces.

This module intentionally contains no provider-specific authentication logic.
Adapters resolve their channel identity into a Principal; authorization is a
separate concern.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Optional


class IdentityMode(str, Enum):
    """How much persistent identity is being used by a capability."""

    ANONYMOUS = "anonymous"
    LOCAL = "local"
    AUTHENTICATED = "authenticated"
    CRYPTOGRAPHIC = "cryptographic"


class AuthenticationMethod(str, Enum):
    """Authentication mechanism, when authentication is actually present."""

    NONE = "none"
    PASSKEY = "passkey"
    OIDC = "oidc"
    VERIFIED_EMAIL = "verified_email"
    VERIFIED_PHONE = "verified_phone"
    CRYPTOGRAPHIC_SIGNATURE = "cryptographic_signature"
    SERVICE_CREDENTIAL = "service_credential"


@dataclass(frozen=True)
class Principal:
    """Normalized caller context passed from interfaces to shared services.

    `principal_id` is deliberately opaque. It must not contain a phone number,
    email address, Telegram identifier, or other directly identifying value.
    """

    principal_id: str
    identity_mode: IdentityMode = IdentityMode.ANONYMOUS
    interface: str = "unknown"
    authentication_method: AuthenticationMethod = AuthenticationMethod.NONE
    session_id: Optional[str] = None
    scopes: FrozenSet[str] = field(default_factory=frozenset)
    capabilities: FrozenSet[str] = field(default_factory=frozenset)

    def is_authenticated(self) -> bool:
        """Return whether this principal has an authenticated identity."""
        return self.identity_mode == IdentityMode.AUTHENTICATED

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities
