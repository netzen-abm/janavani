"""Encrypted durable inbox for Telegram updates plus legacy-payload migration support."""
from __future__ import annotations

import json
import os
from typing import Any, Callable

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

DEFAULT_PAYLOAD_RETENTION_SECONDS = 24 * 60 * 60
MAX_PAYLOAD_RETENTION_SECONDS = 24 * 60 * 60


class PostgresTelegramInbox:
    """Encrypt update bodies before persistence and fence stale worker claims."""

    def __init__(
        self,
        connection_factory: Callable[[], Any] | None = None,
        *,
        dsn: str | None = None,
        encryption_keys: list[str] | None = None,
        payload_retention_seconds: int = DEFAULT_PAYLOAD_RETENTION_SECONDS,
    ) -> None:
        self._dsn = dsn or os.getenv("JANAVANI_TELEGRAM_INBOX_DSN", "").strip()
        self._connection_factory = connection_factory
        if not self._connection_factory and not self._dsn:
            raise ValueError("JANAVANI_TELEGRAM_INBOX_DSN or connection_factory is required")
        if (
            isinstance(payload_retention_seconds, bool)
            or not isinstance(payload_retention_seconds, int)
            or payload_retention_seconds < 60
            or payload_retention_seconds > MAX_PAYLOAD_RETENTION_SECONDS
        ):
            raise ValueError("Telegram inbox payload retention must be between 60 and 86400 seconds")

        raw_keys = encryption_keys
        if raw_keys is None:
            configured = os.getenv("JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS", "").strip()
            raw_keys = [value.strip() for value in configured.split(",") if value.strip()]
        self._fernet = self._build_fernet(raw_keys)
        self._payload_retention_seconds = payload_retention_seconds

    @staticmethod
    def _build_fernet(keys: list[str]) -> MultiFernet | None:
        if not keys:
            return None
        try:
            return MultiFernet([Fernet(key.encode("ascii")) for key in keys])
        except (ValueError, UnicodeEncodeError) as exc:
            raise ValueError(
                "JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS must contain valid Fernet keys"
            ) from exc

    def _require_fernet(self) -> MultiFernet:
        if self._fernet is None:
            raise RuntimeError(
                "JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS is required for durable Telegram payloads"
            )
        return self._fernet

    def _connect(self) -> Any:
        if self._connection_factory:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Psycopg 3 is required for the Telegram inbox") from exc
        return psycopg.connect(self._dsn)

    def accept_encrypted(self, update_id: int, payload: dict[str, Any]) -> bool:
        """Durably enqueue a parsed update as ciphertext with a bounded retention deadline."""
        fernet = self._require_fernet()
        if isinstance(update_id, bool) or not isinstance(update_id, int) or update_id < 0:
            raise ValueError("Telegram update_id must be a non-negative integer")
        if not isinstance(payload, dict) or payload.get("update_id") != update_id:
            raise ValueError("Telegram payload update_id does not match its inbox key")
        serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        encrypted = fernet.encrypt(serialized)
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.telegram_update_inbox
                       (update_id, payload, encrypted_payload, payload_expires_at)
                   VALUES (%s, NULL, %s, now() + (%s * interval '1 second'))
                   ON CONFLICT (update_id) DO NOTHING
                   RETURNING update_id""",
                (update_id, encrypted, self._payload_retention_seconds),
            )
            return cur.fetchone() is not None

    def accept_legacy_payload(self, update_id: int, payload: dict[str, Any]) -> bool:
        """Compatibility/test seam for rows written by the earlier plaintext implementation.

        Production webhook ingress must call accept_encrypted(). Existing plaintext rows
        are encrypted by secure_legacy_payloads() before the worker starts.
        """
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            cur.execute(
                """INSERT INTO public.telegram_update_inbox
                       (update_id, payload, encrypted_payload)
                   VALUES (%s, %s::jsonb, NULL)
                   ON CONFLICT (update_id) DO NOTHING
                   RETURNING update_id""",
                (update_id, json.dumps(payload, separators=(",", ":"))),
            )
            return cur.fetchone() is not None

    def secure_legacy_payloads(self, *, batch_size: int = 100) -> int:
        """Encrypt legacy plaintext rows before the webhook runtime begins accepting work."""
        fernet = self._require_fernet()
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        converted = 0
        while True:
            with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
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
                    serialized = json.dumps(
                        payload, separators=(",", ":"), ensure_ascii=False
                    ).encode("utf-8")
                    encrypted = fernet.encrypt(serialized)
                    cur.execute(
                        """UPDATE public.telegram_update_inbox
                           SET payload = NULL, encrypted_payload = %s,
                               payload_expires_at = LEAST(
                                   COALESCE(payload_expires_at, now() + (%s * interval '1 second')),
                                   now() + (%s * interval '1 second')
                               )
                           WHERE update_id = %s AND payload IS NOT NULL""",
                        (
                            encrypted,
                            self._payload_retention_seconds,
                            self._payload_retention_seconds,
                            update_id,
                        ),
                    )
                    converted += cur.rowcount

    def claim_next(self, *, stale_after_seconds: int = 120) -> dict[str, Any] | None:
        """Claim one unexpired payload; legacy plaintext is encrypted before dispatch."""
        fernet = self._require_fernet()
        with self._connect() as conn, conn.transaction(), conn.cursor() as cur:
            # Expiry is enforced when the worker is running. If it was offline, ciphertext
            # remains unreadable in the database and is cleared on the first maintenance pass.
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
                         AND (payload_expires_at IS NULL OR payload_expires_at > now())
                         AND (
                             (status = 'pending' AND available_at <= now())
                             OR (status = 'processing'
                                 AND locked_at < now() - (%s * interval '1 second'))
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
                # Normally converted during startup; keep compatibility safe if a
                # legacy producer races the one-time conversion.
                serialized = json.dumps(
                    legacy_payload, separators=(",", ":"), ensure_ascii=False
                ).encode("utf-8")
                reencrypted = fernet.encrypt(serialized)
                cur.execute(
                    """UPDATE public.telegram_update_inbox
                       SET payload = NULL, encrypted_payload = %s,
                           payload_expires_at = COALESCE(
                               payload_expires_at, now() + (%s * interval '1 second')
                           )
                       WHERE update_id = %s AND status = 'processing' AND attempts = %s""",
                    (reencrypted, self._payload_retention_seconds, update_id, attempts),
                )
                return {
                    "update_id": update_id,
                    "payload": legacy_payload,
                    "attempts": attempts,
                }

            try:
                plaintext = fernet.decrypt(bytes(encrypted_payload))
                payload = json.loads(plaintext.decode("utf-8"))
                if not isinstance(payload, dict) or payload.get("update_id") != update_id:
                    raise ValueError("decrypted Telegram payload does not match its inbox key")
            except (InvalidToken, ValueError, TypeError, UnicodeDecodeError):
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
