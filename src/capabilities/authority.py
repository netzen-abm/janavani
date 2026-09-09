"""Shared, provider-neutral Authority lookup capability.

Access surfaces must use this boundary for authority resolution rather than
calling provider implementations directly. The capability deliberately keeps
verification and destination requirements explicit so downstream document
composition cannot silently fall back to unverified contacts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.access.authorization import AuthorizationPolicy, AuthorizationRequest
from src.core.authority import AuthorityRecord, AuthorityRepository, require_destination


CAPABILITY_ID = "authority:resolve"


@dataclass(frozen=True)
class AuthorityLookupRequest:
    """Provider-neutral authority lookup parameters."""

    authority_type: str
    city: str
    limit: int = 5


class AuthorityCapability:
    """Canonical application boundary for authority resolution."""

    def __init__(
        self,
        repository: AuthorityRepository,
        *,
        authorization_policy: AuthorizationPolicy | None = None,
    ) -> None:
        self._repository = repository
        self._authorization_policy = authorization_policy or AuthorizationPolicy()

    def get(self, authority_id: str, *, identity: Any) -> AuthorityRecord | None:
        self._authorize(identity=identity, action="read", resource_id=authority_id)
        return self._repository.get(authority_id)

    def search(
        self,
        request: AuthorityLookupRequest,
        *,
        identity: Any,
    ) -> list[AuthorityRecord]:
        self._authorize(identity=identity, action="search")
        return self._repository.search(
            authority_type=request.authority_type,
            city=request.city,
            limit=request.limit,
        )

    def require_verified_destination(
        self,
        authority_id: str,
        *,
        identity: Any,
    ):
        """Resolve an authority and fail closed unless its destination is verified."""
        authority = self.get(authority_id, identity=identity)
        if authority is None:
            raise LookupError("Authority not found")
        if not authority.verified:
            raise ValueError("Authority destination is not verified")
        return require_destination(authority)

    def _authorize(self, *, identity: Any, action: str, resource_id: str | None = None) -> None:
        context = getattr(identity, "authorization_context", identity)
        request = AuthorizationRequest(
            context=context,
            capability=CAPABILITY_ID,
            action=action,
            resource_id=resource_id,
        )
        decision = self._authorization_policy.evaluate(request)
        if not decision.allowed:
            raise PermissionError(f"Authority access denied: {decision.decision.value}")
