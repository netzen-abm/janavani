"""Provider-facing producer facade for the encrypted PostgreSQL Telegram inbox."""
from __future__ import annotations

import os
from typing import Any, Callable

from cryptography.fernet import MultiFernet

from src.storage.repositories.postgres_telegram_inbox_migration import (
    encrypt_legacy_inbox_rows,
)
from src.storage.repositories.postgres_telegram_inbox_worker import (
    PostgresTelegramInboxWorkerStore,
)
from src.storage.telegram_payload_crypto import build_fernet, encrypt_payload, require_fernet

DEFAULT_PAYLOAD_RETENTION_SECONDS = 24 * 60 * 60
MAX_PAYLOAD_RETENTION_SECONDS = 24 * 60 * 60


class PostgresTelegramInbox:
    """Own durable acceptance; delegate worker lease state to its cohesive store."""

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
        self._fernet: MultiFernet | None = build_fernet(raw_keys)
        self._payload_retention_seconds = payload_retention_seconds
        self._worker_store = PostgresTelegramInboxWorkerStore(
            self._connect, self._fernet, payload_retention_seconds
        )

    def _connect(self) -> Any:
        if self._connection_factory:
            return self._connection_factory()
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Psycopg 3 is required for the Telegram inbox") from exc
        # A stalled database connection must not indefinitely delay worker
        # recovery or application shutdown; claim failures are retried by the inbox worker.
        return psycopg.connect(self._dsn, connect_timeout=5)

    def accept_encrypted(self, update_id: int, payload: dict[str, Any]) -> bool:
        """Commit an authenticated encrypted payload before acknowledging delivery."""
        fernet = require_fernet(self._fernet)
        if isinstance(update_id, bool) or not isinstance(update_id, int) or update_id < 0:
            raise ValueError("Telegram update_id must be a non-negative integer")
        if not isinstance(payload, dict) or payload.get("update_id") != update_id:
            raise ValueError("Telegram payload update_id does not match its inbox key")
        encrypted = encrypt_payload(fernet, payload)
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

    def secure_legacy_payloads(self, *, batch_size: int = 100) -> int:
        """Convert legacy plaintext rows before the webhook registers its endpoint."""
        return encrypt_legacy_inbox_rows(
            self._connect,
            require_fernet(self._fernet),
            self._payload_retention_seconds,
            batch_size=batch_size,
        )

    def claim_next(self, *, stale_after_seconds: int = 120) -> dict[str, Any] | None:
        return self._worker_store.claim_next(stale_after_seconds=stale_after_seconds)

    def heartbeat(self, update_id: int, *, attempts: int) -> None:
        self._worker_store.heartbeat(update_id, attempts=attempts)

    def mark_processed(self, update_id: int, *, attempts: int) -> None:
        self._worker_store.mark_processed(update_id, attempts=attempts)

    def retry_or_dead_letter(
        self, update_id: int, *, attempts: int, error_code: str, max_attempts: int = 8
    ) -> None:
        self._worker_store.retry_or_dead_letter(
            update_id, attempts=attempts, error_code=error_code, max_attempts=max_attempts
        )
