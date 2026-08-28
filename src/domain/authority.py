"""Canonical authority references for civic case routing.

Authority records are source-backed references to government organisations/offices.
They remain separate from AI interpretation and transport implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class AuthorityVerificationStatus(str, Enum):
    """Verification state for an authority reference."""

    UNVERIFIED = "unverified"
    CANDIDATE = "candidate"
    VERIFIED = "verified"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class AuthoritySource:
    """Provenance for an authority record."""

    source_id: str
    source_type: str
    uri: str | None = None
    publisher: str | None = None
    retrieved_at: datetime | None = None
    version_or_reference: str | None = None


@dataclass(frozen=True)
class Authority:
    """Canonical government organisation/office reference used by a Case."""

    authority_id: str
    name: str
    authority_type: str
    jurisdiction: dict[str, Any] = field(default_factory=dict)
    organisation_id: str | None = None
    office_id: str | None = None
    postal_addresses: tuple[str, ...] = ()
    contact_points: tuple[str, ...] = ()
    official_urls: tuple[str, ...] = ()
    source_refs: tuple[AuthoritySource, ...] = ()
    verification_status: AuthorityVerificationStatus = (
        AuthorityVerificationStatus.UNVERIFIED
    )
    last_verified_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        name: str,
        authority_type: str,
        *,
        jurisdiction: dict[str, Any] | None = None,
        organisation_id: str | None = None,
        office_id: str | None = None,
        postal_addresses: list[str] | None = None,
        contact_points: list[str] | None = None,
        official_urls: list[str] | None = None,
        source_refs: list[AuthoritySource] | None = None,
        verification_status: AuthorityVerificationStatus = (
            AuthorityVerificationStatus.UNVERIFIED
        ),
        last_verified_at: datetime | None = None,
    ) -> "Authority":
        """Create a validated authority reference."""
        name = name.strip()
        authority_type = authority_type.strip()
        if not name:
            raise ValueError("authority name is required")
        if not authority_type:
            raise ValueError("authority type is required")
        if (
            verification_status == AuthorityVerificationStatus.VERIFIED
            and not source_refs
        ):
            raise ValueError("verified authority requires source references")

        return cls(
            authority_id=f"AUTH-{uuid4().hex[:12].upper()}",
            name=name,
            authority_type=authority_type,
            jurisdiction=dict(jurisdiction or {}),
            organisation_id=organisation_id,
            office_id=office_id,
            postal_addresses=tuple(
                value.strip()
                for value in (postal_addresses or [])
                if value.strip()
            ),
            contact_points=tuple(
                value.strip() for value in (contact_points or []) if value.strip()
            ),
            official_urls=tuple(
                value.strip() for value in (official_urls or []) if value.strip()
            ),
            source_refs=tuple(source_refs or []),
            verification_status=verification_status,
            last_verified_at=last_verified_at,
        )

    def verify(self, *, verified_at: datetime | None = None) -> "Authority":
        """Return a verified copy; provenance is mandatory for verification."""
        if not self.source_refs:
            raise ValueError("cannot verify authority without source references")
        return Authority(
            authority_id=self.authority_id,
            name=self.name,
            authority_type=self.authority_type,
            jurisdiction=dict(self.jurisdiction),
            organisation_id=self.organisation_id,
            office_id=self.office_id,
            postal_addresses=self.postal_addresses,
            contact_points=self.contact_points,
            official_urls=self.official_urls,
            source_refs=self.source_refs,
            verification_status=AuthorityVerificationStatus.VERIFIED,
            last_verified_at=verified_at or datetime.now(timezone.utc),
            created_at=self.created_at,
        )


__all__ = ["Authority", "AuthoritySource", "AuthorityVerificationStatus"]
