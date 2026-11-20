"""PostgreSQL worker-side lease and retry transitions for the Telegram inbox."""
from __future__ import annotations

from typing import Any, Callable

from cryptography.fernet import MultiFernet

from src.storage.telegram_payload_crypto import (
    decrypt_payload,
    encrypt_payload,
    require_fernet,
)


class PostgresTelegramInboxWorkerStore:
    """Keep claim, lease fencing and payload-state transitions in one transaction owner."""

    def __init__(
        self,
        connect: Callable[[], Any],
        fernet: MultiFernet | None,
        payload_retention_seconds: int,
    ) -> None:
        self._connect = connect
        self._fernet = fernet
        self._payload_retention_seconds = payload_retention_seconds

    def claim_next(self, *, stale_after_seconds: int = 120) -> dict[str, Any] | None:
        """Claim one unexpired payload and decrypt it only in worker memory."""
        fernet = require_fernet(self._fernet)
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = 'dead_letter', payload = NULL, encrypted_payload = NULL,
                       payload_expires_at = NULL, locked_at = NULL, processed_at = now(),
                       last_error_code = 'payload_expired'
                   WHERE status IN ('pending', 'processing')
                     AND (payload IS NOT NULL OR encrypted_payload IS NOT NULL)
                     AND payload_expires_at <= now()"""
            )
            cur.execute(
                """WITH candidate AS (
                       SELECT update_id
                       FROM public.telegram_update_inbox
                       WHERE (payload IS NOT NULL OR encrypted_payload IS NOT NULL)
                         AND payload_expires_at > now()
                         AND (
                             (status = 'pending' AND available_at <= now())
                             OR (status = 'processing' AND (
                                 locked_at IS NULL
                                 OR locked_at < now() - (%s * interval '1 second')
                             ))
                         )
                       ORDER BY received_at
                       LIMIT 1
                       FOR UPDATE SKIP LOCKED
                   )
                   UPDATE public.telegram_update_inbox AS inbox
                   SET status = 'processing', attempts = attempts + 1, locked_at = now()
                   FROM candidate
                   WHERE inbox.update_id = candidate.update_id
                   RETURNING inbox.update_id, inbox.payload, inbox.encrypted_payload, inbox.attempts""",
                (stale_after_seconds,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            update_id, legacy_payload, encrypted_payload, attempts = row
            if legacy_payload is not None:
                # Startup converts legacy rows; this protects against an old writer racing it.
                encrypted = encrypt_payload(fernet, legacy_payload)
                cur.execute(
                    """UPDATE public.telegram_update_inbox
                       SET payload = NULL, encrypted_payload = %s,
                           payload_expires_at = COALESCE(
                               payload_expires_at, now() + (%s * interval '1 second')
                           )
                       WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                    (encrypted, self._payload_retention_seconds, update_id, attempts),
                )
                return {"update_id": update_id, "payload": legacy_payload, "attempts": attempts}
            try:
                payload = decrypt_payload(fernet, update_id, encrypted_payload)
            except (ValueError, TypeError):
                cur.execute(
                    """UPDATE public.telegram_update_inbox
                       SET status = 'dead_letter', payload = NULL, encrypted_payload = NULL,
                           payload_expires_at = NULL, locked_at = NULL, processed_at = now(),
                           last_error_code = 'payload_decryption_failed'
                       WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                    (update_id, attempts),
                )
                return None
            return {"update_id": update_id, "payload": payload, "attempts": attempts}

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
                   SET status = 'processed', payload = NULL, encrypted_payload = NULL,
                       payload_expires_at = NULL, locked_at = NULL, processed_at = now(),
                       last_error_code = NULL
                   WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                (update_id, attempts),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox update was not owned by this worker")

    def retry_or_dead_letter(
        self, update_id: int, *, attempts: int, error_code: str, max_attempts: int = 8
    ) -> None:
        """Retry with bounded backoff; terminal rows do not retain message payloads."""
        terminal = attempts >= max_attempts
        delay = min(300, 2 ** min(attempts, 8))
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = %s,
                       payload = CASE WHEN %s THEN NULL ELSE payload END,
                       encrypted_payload = CASE WHEN %s THEN NULL ELSE encrypted_payload END,
                       payload_expires_at = CASE WHEN %s THEN NULL ELSE payload_expires_at END,
                       available_at = now() + (%s * interval '1 second'),
                       locked_at = NULL,
                       processed_at = CASE WHEN %s THEN now() ELSE NULL END,
                       last_error_code = %s
                   WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                (
                    "dead_letter" if terminal else "pending",
                    terminal,
                    terminal,
                    terminal,
                    delay,
                    terminal,
                    error_code[:80],
                    update_id,
                    attempts,
                ),
            )
            if cur.rowcount != 1:
                raise RuntimeError("Telegram inbox update was not owned by this worker")
