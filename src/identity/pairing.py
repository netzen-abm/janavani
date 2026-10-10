"""Explicit, expiring Web↔Telegram identity pairing.

The web principal initiates a challenge; Telegram claims it; the authenticated
web principal must confirm the Telegram subject before a verified link is saved.
Only a digest of the one-time code is persisted. This module owns the pairing
trust boundary; surface handlers remain thin adapters.
"""
from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Protocol

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

    def __init__(self) -> None:
        self._items: dict[str, _PendingPairing] = {}

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
        return ExternalIdentity(
            provider=item.provider, subject=item.subject, principal_id=item.principal_id,
            authentication_method="web_telegram_pairing", verified=True,
        )


class PostgresPairingRepository:
    """PostgreSQL adapter; each state transition is row-locked and transactional."""

    def __init__(self, connection_factory: Callable[[], Any] | None = None, *, dsn: str | None = None) -> None:
        self._dsn = dsn or os.getenv("JANAVANI_IDENTITY_LINKS_DSN", "").strip()
        self._connection_factory = connection_factory
        if not self._connection_factory and not self._dsn:
            raise ValueError("JANAVANI_IDENTITY_LINKS_DSN or connection_factory is required")

    def _connect(self) -> Any:
        if self._connection_factory:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Psycopg 3 is required for PostgreSQL identity pairing") from exc
        return psycopg.connect(self._dsn)

    def issue(self, pairing_id: str, token_digest: str, principal_id: str, expires_at: datetime) -> None:
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.external_identity_pairings
                   (pairing_id, token_digest, principal_id, expires_at)
                   VALUES (%s, %s, %s, %s)""",
                (pairing_id, token_digest, principal_id, expires_at),
            )

    def claim(self, token_digest: str, provider: str, subject: str, now: datetime) -> PairingClaim | None:
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """SELECT pairing_id, principal_id, expires_at, provider, subject
                   FROM public.external_identity_pairings
                   WHERE token_digest = %s FOR UPDATE""",
                (token_digest,),
            )
            row = cur.fetchone()
            if row is None or row[2] <= now or row[3] is not None:
                return None
            cur.execute(
                """UPDATE public.external_identity_pairings
                   SET provider = %s, subject = %s, claimed_at = %s
                   WHERE pairing_id = %s AND provider IS NULL""",
                (provider, subject, now, row[0]),
            )
            if cur.rowcount != 1:
                return None
            return PairingClaim(row[0], row[1], provider, subject, row[2])

    def confirm(self, pairing_id: str, principal_id: str, now: datetime) -> ExternalIdentity | None:
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """SELECT principal_id, provider, subject, expires_at, confirmed_at
                   FROM public.external_identity_pairings
                   WHERE pairing_id = %s FOR UPDATE""",
                (pairing_id,),
            )
            row = cur.fetchone()
            if (
                row is None or row[0] != principal_id or row[3] <= now
                or row[1] != "telegram" or not row[2] or row[4] is not None
            ):
                return None
            cur.execute(
                """INSERT INTO public.external_identity_links
                   (provider, subject, principal_id, authentication_method, verified)
                   VALUES (%s, %s, %s, 'web_telegram_pairing', true)
                   ON CONFLICT (provider, subject) DO NOTHING""",
                (row[1], row[2], row[0]),
            )
            if cur.rowcount != 1:
                cur.execute(
                    """SELECT principal_id, verified FROM public.external_identity_links
                       WHERE provider = %s AND subject = %s""",
                    (row[1], row[2]),
                )
                existing = cur.fetchone()
                if existing is None or existing[0] != row[0] or not existing[1]:
                    raise PermissionError("Telegram identity is already linked to another principal")
            cur.execute(
                """UPDATE public.external_identity_pairings SET confirmed_at = %s
                   WHERE pairing_id = %s AND confirmed_at IS NULL""",
                (now, pairing_id),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Pairing confirmation lost its single-use race")
            return ExternalIdentity(
                provider=row[1], subject=row[2], principal_id=row[0],
                authentication_method="web_telegram_pairing", verified=True,
            )


def _digest(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _utc(value: datetime | None) -> datetime:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Pairing timestamps must be timezone-aware")
    return current.astimezone(timezone.utc)
