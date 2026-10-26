"""PostgreSQL persistence adapter for Web↔Telegram identity pairing."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Callable

from src.identity.external import ExternalIdentity
from src.identity.pairing import PairingClaim


class PostgresPairingRepository:
    """Row-lock each pairing transition and commit link + confirmation atomically."""

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
            return PairingClaim(row[0], row[1], provider, subject, row[2]) if cur.rowcount == 1 else None

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
