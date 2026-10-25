"""PostgreSQL receipt ledger plus compatibility support for legacy payload rows."""
from __future__ import annotations

import json
import os
from typing import Any, Callable


class PostgresTelegramInbox:
    """Fence stale worker claims; new webhook receipts contain no payload."""

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

    def accept_legacy_payload(self, update_id: int, payload: dict[str, Any]) -> bool:
        """Compatibility-only enqueue for draining pre-existing payload-bearing inbox work.

        New webhook deliveries must use claim_update() and never write their message
        body to durable storage. Keep this method explicit so it is not mistaken for
        the preferred acceptance path.
        """
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.telegram_update_inbox (update_id, payload)
                   VALUES (%s, %s::jsonb) ON CONFLICT (update_id) DO NOTHING
                   RETURNING update_id""",
                (update_id, json.dumps(payload, separators=(",", ":"))),
            )
            return cur.fetchone() is not None

    def claim_update(
        self, update_id: int, *, stale_after_seconds: int = 120
    ) -> dict[str, Any]:
        """Claim an inline webhook receipt without durably storing its payload."""
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.telegram_update_inbox
                       (update_id, payload, status, attempts, locked_at)
                   VALUES (%s, NULL, 'processing', 1, now())
                   ON CONFLICT (update_id) DO NOTHING
                   RETURNING attempts""",
                (update_id,),
            )
            inserted = cur.fetchone()
            if inserted is not None:
                return {"status": "claimed", "attempts": inserted[0]}

            cur.execute(
                """SELECT status, attempts, payload IS NOT NULL,
                          (locked_at >= now() - (%s * interval '1 second')),
                          (available_at > now())
                   FROM public.telegram_update_inbox
                   WHERE update_id = %s
                   FOR UPDATE""",
                (stale_after_seconds, update_id),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("Telegram inbox receipt disappeared during claim")

            status, attempts, has_payload, lease_active, retry_wait = row
            if status in {"processed", "dead_letter"}:
                return {"status": status, "attempts": attempts}
            if has_payload:
                # Compatibility-only rows were accepted by the old durable-payload
                # path and must be drained by the legacy worker, not dispatched twice.
                return {"status": "legacy_payload", "attempts": attempts}
            if status == "processing" and lease_active:
                return {"status": "busy", "attempts": attempts}
            if status == "pending" and retry_wait:
                return {"status": "busy", "attempts": attempts}

            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = 'processing', attempts = attempts + 1,
                       locked_at = now(), available_at = now()
                   WHERE update_id = %s AND payload IS NULL
                     AND status IN ('pending', 'processing')
                   RETURNING attempts""",
                (update_id,),
            )
            claimed = cur.fetchone()
            if claimed is None:
                return {"status": "busy", "attempts": attempts}
            return {"status": "claimed", "attempts": claimed[0]}

    def claim_next(self, *, stale_after_seconds: int = 120) -> dict[str, Any] | None:
        """Claim one payload-bearing legacy update; receipt-only rows run inline."""
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """WITH candidate AS (
                       SELECT update_id FROM public.telegram_update_inbox
                       WHERE payload IS NOT NULL AND (
                             (status = 'pending' AND available_at <= now())
                             OR (status = 'processing'
                                 AND locked_at < now() - (%s * interval '1 second'))
                         )
                       ORDER BY received_at
                       LIMIT 1 FOR UPDATE SKIP LOCKED
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

    def heartbeat(self, update_id: int, *, attempts: int) -> None:
        """Renew only the current claim; a reclaimed claim fences the old worker."""
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox SET locked_at = now()
                   WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                (update_id, attempts),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox processing lease was lost")

    def mark_processed(self, update_id: int, *, attempts: int) -> None:
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = 'processed', payload = NULL, locked_at = NULL,
                       processed_at = now(), last_error_code = NULL
                   WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                (update_id, attempts),
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
                   WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                ("dead_letter" if terminal else "pending", terminal, delay, terminal,
                 error_code[:80], update_id, attempts),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox update was not owned by this worker")
