"""Canonical consent domain object for optional and authorized data use."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class ConsentGrantType(str, Enum):
    EXPLICIT = "explicit"
    REQUIRED_BY_DESTINATION = "required_by_destination"
    NOT_REQUIRED = "not_required"


class ConsentStatus(str, Enum):
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Consent:
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
            raise ValueError("scope must not be empty for required consent")
        if not self.created_at.strip():
            raise ValueError("created_at must not be empty")
        if self.status is ConsentStatus.REVOKED and not self.revoked_at:
            raise ValueError("revoked_at is required for revoked consent")

    @property
    def is_authorized(self) -> bool:
        """Return whether this grant is currently active; malformed expiry fails closed."""
        return self.is_authorized_at()

    def is_authorized_at(self, now: datetime | None = None) -> bool:
        """Evaluate grant status and expiry against an injectable UTC instant."""
        if self.status is not ConsentStatus.GRANTED:
            return False
        if self.expires_at is None:
            return True
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
            instant = now or datetime.now(timezone.utc)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if instant.tzinfo is None:
                instant = instant.replace(tzinfo=timezone.utc)
            return instant < expiry
        except (TypeError, ValueError, AttributeError):
            return False

    def authorizes(self, purpose: str, scope: str, *, now: datetime | None = None) -> bool:
        return (
            self.is_authorized_at(now)
            and self.purpose == purpose
            and scope in self.scope
        )
