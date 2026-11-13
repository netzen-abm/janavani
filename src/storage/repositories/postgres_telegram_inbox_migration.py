"""One-time data migration from legacy plaintext Telegram inbox rows."""
from __future__ import annotations

from typing import Any, Callable

from cryptography.fernet import MultiFernet

from src.storage.telegram_payload_crypto import encrypt_payload


def encrypt_legacy_inbox_rows(
    connect: Callable[[], Any],
    fernet: MultiFernet,
    retention_seconds: int,
    *,
    batch_size: int = 100,
) -> int:
    """Encrypt legacy rows in bounded batches before the webhook accepts new work."""
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
        raise ValueError("batch_size must be a positive integer")
    converted = 0
    while True:
        with connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """UPDATE public.telegram_update_inbox
                   SET status = 'dead_letter', payload = NULL, encrypted_payload = NULL,
                       payload_expires_at = NULL, locked_at = NULL, processed_at = now(),
                       last_error_code = 'payload_expired'
                   WHERE status IN ('pending', 'processing')
                     AND payload IS NOT NULL AND payload_expires_at <= now()"""
            )
            cur.execute(
                """SELECT update_id, payload
                   FROM public.telegram_update_inbox
                   WHERE payload IS NOT NULL
                   ORDER BY received_at
                   LIMIT %s
                   FOR UPDATE SKIP LOCKED""",
                (batch_size,),
            )
            rows = cur.fetchall()
            if not rows:
                return converted
            for update_id, payload in rows:
                encrypted = encrypt_payload(fernet, payload)
                cur.execute(
                    """UPDATE public.telegram_update_inbox
                       SET payload = NULL, encrypted_payload = %s,
                           payload_expires_at = LEAST(
                               COALESCE(payload_expires_at, now() + (%s * interval '1 second')),
                               now() + (%s * interval '1 second')
                           )
                       WHERE update_id = %s AND payload IS NOT NULL""",
                    (encrypted, retention_seconds, retention_seconds, update_id),
                )
                converted += cur.rowcount
