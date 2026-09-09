"""Shared, provider-neutral Authority lookup capability.

Authority metadata is public destination data. Authorization remains enforced
at the owned Case and action boundaries; this capability prevents access
surfaces from coupling directly to provider repositories.
"""
from __future__ import annotations

from dataclasses import dataclass

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

    def __init__(self, repository: AuthorityRepository) -> None:
        self._repository = repository

    def get(self, authority_id: str) -> AuthorityRecord | None:
        return self._repository.get(authority_id)

    def search(self, request: AuthorityLookupRequest) -> list[AuthorityRecord]:
        if request.limit < 1:
            return []
        return self._repository.search(
            authority_type=request.authority_type,
            city=request.city,
            limit=request.limit,
        )

    def require_verified_destination(self, authority_id: str):
        """Resolve an authority and fail closed unless its destination is verified."""
        authority = self.get(authority_id)
        if authority is None:
            raise LookupError("Authority not found")
        if not authority.verified:
            raise ValueError("Authority destination is not verified")
        return require_destination(authority)
