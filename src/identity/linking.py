"""Shared external-identity linking contract and fail-closed implementation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .external import ExternalIdentity

@dataclass(frozen=True)
class IdentityLinkRequest:
    principal_id: str
    provider: str
    subject: str
    authentication_method: str

class ExternalIdentityLinkRepository(Protocol):
    def find(self, provider: str, subject: str) -> ExternalIdentity | None: ...
    def save(self, identity: ExternalIdentity) -> None: ...

class InMemoryExternalIdentityLinkRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], ExternalIdentity] = {}
    def find(self, provider: str, subject: str) -> ExternalIdentity | None:
        return self._items.get((provider, subject))
    def save(self, identity: ExternalIdentity) -> None:
        key = (identity.provider, identity.subject)
        existing = self._items.get(key)
        if existing is not None and existing.principal_id != identity.principal_id:
            raise ValueError("external identity is already linked to another principal")
        self._items[key] = identity

class IdentityLinkingService:
    def __init__(self, repository: ExternalIdentityLinkRepository) -> None:
        self._repository = repository
    def link_verified(self, request: IdentityLinkRequest, *, verified: bool) -> ExternalIdentity:
        if not verified:
            raise PermissionError("explicit verified identity linking is required")
        if not request.principal_id or not request.provider or not request.subject or request.authentication_method == "none":
            raise ValueError("principal, provider, subject and authentication method are required")
        existing = self._repository.find(request.provider, request.subject)
        if existing is not None and existing.principal_id != request.principal_id:
            raise PermissionError("external identity is already linked to another principal")
        identity = ExternalIdentity(
            provider=request.provider, subject=request.subject,
            principal_id=request.principal_id,
            authentication_method=request.authentication_method, verified=True,
        )
        self._repository.save(identity)
        return identity

class IdentityLinkResolver:
    """Resolve a provider subject only after an explicit verified link exists."""

    def __init__(self, repository: ExternalIdentityLinkRepository) -> None:
        self._repository = repository

    def resolve(self, provider: str, subject: str) -> ExternalIdentity:
        identity = self._repository.find(provider, subject)
        if identity is None or not identity.is_usable():
            raise LookupError("external identity is not explicitly linked and verified")
        return identity

