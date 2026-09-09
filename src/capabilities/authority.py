"""Shared, provider-neutral Authority lookup capability.

Access surfaces must use this boundary for authority resolution rather than
calling provider implementations directly. Verification and destination
requirements remain explicit so downstream document composition cannot silently
fall back to unverified contacts.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.authority import AuthorityRecord, AuthorityRepository, require_destination
from src.identity.context import IdentityContext


CAPABILITY_ID = "authority:resolve"


@dataclass(frozen=True)
class AuthorityLookupRequest:
    """Provider-neutral authority lookup parameters."""

    authority_type: str
    city: str
    limit: int = 5


class AuthorityCapability:
    """Canonical application boundary for authority resolution."""

    def __init__(self, repository: AuthorityRepository) -> None:
        self._repository = repository

    def get(self, authority_id: str, *, identity: IdentityContext) -> AuthorityRecord | None:
        self._authorize(identity, "authority:read", resource_id=authority_id)
        return self._repository.get(authority_id)

    def search(self, request: AuthorityLookupRequest, *, identity: IdentityContext) -> list[AuthorityRecord]:
        self._authorize(identity, "authority:search")
        if request.limit < 1:
            return []
        return self._repository.search(
            authority_type=request.authority_type,
            city=request.city,
            limit=request.limit,
        )

    def require_verified_destination(self, authority_id: str, *, identity: IdentityContext):
        """Resolve an authority and fail closed unless its destination is verified."""
        authority = self.get(authority_id, identity=identity)
        if authority is None:
            raise LookupError("Authority not found")
        if not authority.verified:
            raise ValueError("Authority destination is not verified")
        return require_destination(authority)

    @staticmethod
    def _authorize(identity: IdentityContext, action: str, *, resource_id: str | None = None) -> None:
        decision = authorize(
            AuthorizationRequest(
                context=identity,
                capability=CAPABILITY_ID,
                action=action,
                resource_id=resource_id,
            )
        )
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized for authority access")
