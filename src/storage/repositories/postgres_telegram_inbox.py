"""PostgreSQL-backed idempotent inbox for Telegram webhook updates."""
from __future__ import annotations

import json
import os
from typing import Any, Callable


class PostgresTelegramInbox:
    """Persist accepted updates and recover stale claims after worker restart."""

    def __init__(
        self, connection_factory: Callable[[], Any] | None = None, *, dsn: str | None = None
    ) -> None:
        self._dsn = dsn or os.getenv("JANAVANI_TELEGRAM_INBOX_DSN", "").strip()
        self._connection_factory = connection_factory
        if not self._connection_factory and not self._dsn:
            raise ValueError("JANAVANI_TELEGRAM_INBOX_DSN or connection_factory is required")

    def _connect(self) -> Any:
        if self._connection_factory:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Psycopg 3 is required for the Telegram inbox") from exc
        return psycopg.connect(self._dsn)

    def accept(self, update_id: int, payload: dict[str, Any]) -> bool:
        """Return True for new durable work, False for a previously accepted ID."""
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.telegram_update_inbox (update_id, payload)
                   VALUES (%s, %s::jsonb) ON CONFLICT (update_id) DO NOTHING
                   RETURNING update_id""",
                (update_id, json.dumps(payload, separators=(",", ":"))),
            )
            return cur.fetchone() is not None

    def claim_next(self, *, stale_after_seconds: int = 120) -> dict[str, Any] | None:
        """Claim one available update; reclaim work abandoned by a crashed worker."""
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """WITH candidate AS (
                       SELECT update_id FROM public.telegram_update_inbox
                       WHERE (status = 'pending' AND available_at <= now())
                          OR (status = 'processing'
                              AND locked_at < now() - (%s * interval '1 second'))
                       ORDER BY received_at
                       FOR UPDATE SKIP LOCKED LIMIT 1
                   )
                   UPDATE public.telegram_update_inbox AS inbox
                   SET status = 'processing', attempts = attempts + 1, locked_at = now()
                   FROM candidate WHERE inbox.update_id = candidate.update_id
                   RETURNING inbox.update_id, inbox.payload, inbox.attempts""",
                (stale_after_seconds,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {"update_id": row[0], "payload": row[1], "attempts": row[2]}

    def heartbeat(self, update_id: int) -> None:
        """Extend a live processing lease so long handlers are not reclaimed."""
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox SET locked_at = now()
                   WHERE update_id = %s AND status = 'processing'""",
                (update_id,),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox processing lease was lost")

    def mark_processed(self, update_id: int) -> None:
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = 'processed', payload = NULL, locked_at = NULL,
                       processed_at = now(), last_error_code = NULL
                   WHERE update_id = %s AND status = 'processing'""",
                (update_id,),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox update was not owned by this worker")

    def retry_or_dead_letter(
        self, update_id: int, *, attempts: int, error_code: str, max_attempts: int = 8
    ) -> None:
        """Retry with bounded backoff; terminal rows never retain message payloads."""
        terminal = attempts >= max_attempts
        delay = min(300, 2 ** min(attempts, 8))
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = %s, payload = CASE WHEN %s THEN NULL ELSE payload END,
                       available_at = now() + (%s * interval '1 second'),
                       locked_at = NULL, processed_at = CASE WHEN %s THEN now() ELSE NULL END,
                       last_error_code = %s
                   WHERE update_id = %s AND status = 'processing'""",
                ("dead_letter" if terminal else "pending", terminal, delay, terminal,
                 error_code[:80], update_id),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox update was not owned by this worker")
