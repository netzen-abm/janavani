"""Canonical consent and approval primitives.

Consent is purpose-bound and does not itself imply successful execution.
Authorization enforcement remains an application/API responsibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class ConsentStatus(str, Enum):
    """Lifecycle status for a consent record."""

    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True)
class Consent:
    """Purpose-bound authorization evidence for a case capability."""

    consent_id: str
    subject_id: str
    capability_id: str
    purpose: str
    scope: tuple[str, ...]
    data_categories: tuple[str, ...]
    status: ConsentStatus
    policy_version: str
    source_channel: str
    granted_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    proof_ref: str | None = None

    @classmethod
    def grant(
        cls,
        subject_id: str,
        capability_id: str,
        purpose: str,
        *,
        scope: list[str] | tuple[str, ...] = (),
        data_categories: list[str] | tuple[str, ...] = (),
        policy_version: str = "v1",
        source_channel: str,
        expires_at: datetime | None = None,
        proof_ref: str | None = None,
    ) -> "Consent":
        """Create an active, purpose-bound consent record."""
        if not subject_id.strip():
            raise ValueError("subject_id is required")
        if not capability_id.strip():
            raise ValueError("capability_id is required")
        if not purpose.strip():
            raise ValueError("purpose is required")
        if not source_channel.strip():
            raise ValueError("source_channel is required")
        return cls(
            consent_id=f"CON-{uuid4().hex[:12].upper()}",
            subject_id=subject_id.strip(),
            capability_id=capability_id.strip(),
            purpose=purpose.strip(),
            scope=tuple(x.strip() for x in scope if x.strip()),
            data_categories=tuple(x.strip() for x in data_categories if x.strip()),
            status=ConsentStatus.GRANTED,
            policy_version=policy_version,
            source_channel=source_channel.strip(),
            granted_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            proof_ref=proof_ref,
        )

    def is_active(self, *, now: datetime | None = None) -> bool:
        """Return whether consent is currently active."""
        now = now or datetime.now(timezone.utc)
        if self.status != ConsentStatus.GRANTED:
            return False
        return self.expires_at is None or self.expires_at > now

    def revoke(self, *, at: datetime | None = None) -> "Consent":
        """Return a copy marked as revoked."""
        return Consent(
            consent_id=self.consent_id,
            subject_id=self.subject_id,
            capability_id=self.capability_id,
            purpose=self.purpose,
            scope=self.scope,
            data_categories=self.data_categories,
            status=ConsentStatus.REVOKED,
            policy_version=self.policy_version,
            source_channel=self.source_channel,
            granted_at=self.granted_at,
            expires_at=self.expires_at,
            revoked_at=at or datetime.now(timezone.utc),
            proof_ref=self.proof_ref,
        )


__all__ = ["Consent", "ConsentStatus"]
