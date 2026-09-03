"""Channel-neutral authority and office destination contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class AuthorityContact:
    """A public/professional contact point for an authority."""

    name: str
    address: str = ""
    email: str | None = None
    role: str | None = None
    source_ref: str | None = None
    verified: bool = False


@dataclass(frozen=True)
class AuthorityRecord:
    """Canonical authority record used by civic capabilities."""

    authority_id: str
    name: str
    authority_type: str
    jurisdiction: dict[str, str] = field(default_factory=dict)
    primary_contact: AuthorityContact | None = None
    cc_contacts: tuple[AuthorityContact, ...] = field(default_factory=tuple)
    source_refs: tuple[str, ...] = field(default_factory=tuple)
    verification_status: str = "UNVERIFIED"
    last_verified_at: str | None = None

    @property
    def verified(self) -> bool:
        return self.verification_status == "VERIFIED"


class AuthorityRepository(Protocol):
    """Provider-neutral authority lookup contract."""

    def get(self, authority_id: str) -> AuthorityRecord | None:
        ...

    def search(
        self,
        *,
        authority_type: str,
        city: str,
        limit: int = 5,
    ) -> list[AuthorityRecord]:
        ...


def require_destination(authority: AuthorityRecord) -> AuthorityContact:
    """Return a usable destination or fail closed."""
    if authority.primary_contact is None:
        raise ValueError("Authority has no destination contact")
    return authority.primary_contact
