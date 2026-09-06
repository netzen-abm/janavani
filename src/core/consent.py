"""Canonical consent domain object for optional and authorized data use.

Consent is explicit domain state, not an inferred property of access,
authentication, case creation, or a consent reference string.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConsentGrantType(str, Enum):
    """Canonical mechanisms by which a consent requirement is satisfied."""

    EXPLICIT = "explicit"
    REQUIRED_BY_DESTINATION = "required_by_destination"
    NOT_REQUIRED = "not_required"


class ConsentStatus(str, Enum):
    """Current authoritative state of a consent record."""

    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Consent:
    """A purpose- and scope-bound consent record."""

    consent_id: str
    subject_id: str
    purpose: str
    scope: tuple[str, ...]
    grant_type: ConsentGrantType
    status: ConsentStatus
    created_at: str
    expires_at: str | None = None
    revoked_at: str | None = None
    proof_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.consent_id.strip():
            raise ValueError("consent_id must not be empty")
        if not self.subject_id.strip():
            raise ValueError("subject_id must not be empty")
        if not self.purpose.strip():
            raise ValueError("purpose must not be empty")
        if not self.scope and self.grant_type is not ConsentGrantType.NOT_REQUIRED:
            raise ValueError("scope must not be empty for granted consent")
        if not self.created_at.strip():
            raise ValueError("created_at must not be empty")
        if self.status is ConsentStatus.REVOKED and not self.revoked_at:
            raise ValueError("revoked_at is required for revoked consent")

    @property
    def is_authorized(self) -> bool:
        """Return whether the consent is currently usable for its scope."""
        return self.status is ConsentStatus.GRANTED

    def authorizes(self, purpose: str, scope: str) -> bool:
        """Check current consent state for one purpose/scope pair."""
        return (
            self.is_authorized
            and self.purpose == purpose
            and scope in self.scope
        )
