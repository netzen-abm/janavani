"""Explicit, expiring Web↔Telegram identity pairing.

The web principal initiates a challenge; Telegram claims it; the authenticated
web principal must confirm the Telegram subject before a verified link is saved.
Only a digest of the one-time code is persisted. This module owns the pairing
trust boundary; surface handlers remain thin adapters.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from src.identity.external import ExternalIdentity


@dataclass(frozen=True)
class PairingChallenge:
    pairing_id: str
    code: str
    expires_at: datetime


@dataclass(frozen=True)
class PairingClaim:
    pairing_id: str
    principal_id: str
    provider: str
    subject: str
    expires_at: datetime


class PairingRepository(Protocol):
    def issue(self, pairing_id: str, token_digest: str, principal_id: str, expires_at: datetime) -> None: ...
    def claim(self, token_digest: str, provider: str, subject: str, now: datetime) -> PairingClaim | None: ...
    def confirm(self, pairing_id: str, principal_id: str, now: datetime) -> ExternalIdentity | None: ...


class IdentityPairingService:
    """Use a two-party confirmation ceremony to link Web and Telegram identities."""

    def __init__(self, repository: PairingRepository, *, lifetime: timedelta = timedelta(minutes=5)) -> None:
        if lifetime <= timedelta(0) or lifetime > timedelta(minutes=10):
            raise ValueError("Pairing lifetime must be greater than zero and at most ten minutes")
        self._repository = repository
        self._lifetime = lifetime

    def issue(self, *, principal_id: str, now: datetime | None = None) -> PairingChallenge:
        principal = principal_id.strip()
        if not principal:
            raise ValueError("Authenticated principal is required")
        issued = _utc(now)
        code = secrets.token_urlsafe(16)
        pairing_id = secrets.token_urlsafe(18)
        expires_at = issued + self._lifetime
        self._repository.issue(pairing_id, _digest(code), principal, expires_at)
        return PairingChallenge(pairing_id, code, expires_at)

    def claim_telegram(self, code: str, *, telegram_subject: str, now: datetime | None = None) -> PairingClaim:
        normalized = code.strip()
        subject = telegram_subject.strip()
        if not normalized or not subject:
            raise ValueError("Pairing code and authenticated Telegram subject are required")
        claim = self._repository.claim(_digest(normalized), "telegram", subject, _utc(now))
        if claim is None:
            raise LookupError("Pairing code is invalid, expired, or already used")
        return claim

    def confirm_from_web(
        self, pairing_id: str, *, principal_id: str, explicit_confirmation: bool,
        now: datetime | None = None,
    ) -> ExternalIdentity:
        if not explicit_confirmation:
            raise PermissionError("Explicit confirmation in the authenticated WebApp is required")
        principal = principal_id.strip()
        if not principal:
            raise PermissionError("Authenticated principal is required")
        identity = self._repository.confirm(pairing_id, principal, _utc(now))
        if identity is None:
            raise LookupError("Pairing is missing, expired, unclaimed, or belongs to another principal")
        return identity


@dataclass
class _PendingPairing:
    pairing_id: str
    token_digest: str
    principal_id: str
    expires_at: datetime
    provider: str | None = None
    subject: str | None = None
    claimed_at: datetime | None = None
    confirmed_at: datetime | None = None


class InMemoryPairingRepository:
    """Deterministic adapter for unit tests and local development only."""

    def __init__(self, identity_link_repository=None) -> None:
        self._items: dict[str, _PendingPairing] = {}
        self._identity_link_repository = identity_link_repository

    def issue(self, pairing_id: str, token_digest: str, principal_id: str, expires_at: datetime) -> None:
        self._items[pairing_id] = _PendingPairing(pairing_id, token_digest, principal_id, expires_at)

    def claim(self, token_digest: str, provider: str, subject: str, now: datetime) -> PairingClaim | None:
        for item in self._items.values():
            if item.token_digest != token_digest or item.expires_at <= now:
                continue
            if item.provider is not None or item.confirmed_at is not None:
                return None
            item.provider, item.subject, item.claimed_at = provider, subject, now
            return PairingClaim(item.pairing_id, item.principal_id, provider, subject, item.expires_at)
        return None

    def confirm(self, pairing_id: str, principal_id: str, now: datetime) -> ExternalIdentity | None:
        item = self._items.get(pairing_id)
        if (
            item is None or item.principal_id != principal_id or item.expires_at <= now
            or item.provider != "telegram" or not item.subject or item.confirmed_at is not None
        ):
            return None
        item.confirmed_at = now
        identity = ExternalIdentity(
            provider=item.provider, subject=item.subject, principal_id=item.principal_id,
            authentication_method="web_telegram_pairing", verified=True,
        )
        if self._identity_link_repository is not None:
            self._identity_link_repository.save(identity)
        return identity



def _digest(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _utc(value: datetime | None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Pairing timestamps must be timezone-aware")
    return current.astimezone(timezone.utc)
