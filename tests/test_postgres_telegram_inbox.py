import base64
import json
import os
import time
from pathlib import Path

import pytest

from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
TEST_FERNET_KEY = base64.urlsafe_b64encode(b"0" * 32).decode("ascii")
MIGRATIONS = (
    ROOT / "db/migrations/20261012120000_telegram_update_inbox.sql",
    ROOT / "db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql",
)


def _apply_migrations(dsn: str) -> None:
    import psycopg

    with psycopg.connect(dsn) as conn:
        for migration_path in MIGRATIONS:
            conn.execute(migration_path.read_text(encoding="utf-8"))


def _inbox(dsn: str = DSN) -> PostgresTelegramInbox:
    return PostgresTelegramInbox(dsn=dsn, encryption_keys=[TEST_FERNET_KEY])


def test_postgres_connection_uses_bounded_connect_timeout(monkeypatch):
    import sys
    from types import SimpleNamespace

    observed = {}

    def fake_connect(dsn, **kwargs):
        observed["dsn"] = dsn
        observed.update(kwargs)
        return object()

    monkeypatch.setitem(sys.modules, "psycopg", SimpleNamespace(connect=fake_connect))
    inbox = PostgresTelegramInbox(
        dsn="postgresql://unit-test.invalid/janavani",
        encryption_keys=[TEST_FERNET_KEY],
    )

    assert inbox._connect() is not None
    assert observed["dsn"] == "postgresql://unit-test.invalid/janavani"
    assert observed["connect_timeout"] == 5


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_encrypted_queue_never_persists_plaintext_and_deduplicates():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    marker = "synthetic-citizen-narrative-must-not-be-plaintext"
    payload = {
        "update_id": update_id,
        "message": {"text": marker},
    }
    _apply_migrations(DSN)
    inbox = _inbox()
    try:
        assert inbox.accept_encrypted(update_id, payload) is True
        assert inbox.accept_encrypted(update_id, payload) is False

        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                """SELECT status, payload, encrypted_payload, payload_expires_at
                   FROM public.telegram_update_inbox WHERE update_id = %s""",
                (update_id,),
            ).fetchone()
        assert row[0] == "pending"
        assert row[1] is None
        assert row[2] is not None
        assert marker.encode() not in bytes(row[2])
        assert row[3] is not None

        first = inbox.claim_next()
        assert first is not None
        assert first["update_id"] == update_id
        assert first["payload"] == payload
        assert first["attempts"] == 1
        assert inbox.claim_next() is None

        inbox.mark_processed(update_id, attempts=first["attempts"])
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                """SELECT status, payload, encrypted_payload, payload_expires_at
                   FROM public.telegram_update_inbox WHERE update_id = %s""",
                (update_id,),
            ).fetchone()
        assert row == ("processed", None, None, None)
        assert inbox.accept_encrypted(update_id, payload) is False
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_encrypted_queue_fences_a_reclaimed_worker():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    payload = {"update_id": update_id, "message": {"text": "lease-fence-test"}}
    _apply_migrations(DSN)
    inbox = _inbox()
    try:
        assert inbox.accept_encrypted(update_id, payload)
        first = inbox.claim_next()
        assert first is not None and first["update_id"] == update_id
        with psycopg.connect(DSN) as conn:
            conn.execute(
                """UPDATE public.telegram_update_inbox
                   SET locked_at = now() - interval '5 minutes'
                   WHERE update_id = %s""",
                (update_id,),
            )
        second = inbox.claim_next(stale_after_seconds=1)
        assert second is not None and second["update_id"] == update_id
        assert second["attempts"] == first["attempts"] + 1
        assert second["payload"] == payload
        with pytest.raises(RuntimeError, match="lease was lost"):
            inbox.heartbeat(update_id, attempts=first["attempts"])
        with pytest.raises(RuntimeError, match="not owned"):
            inbox.mark_processed(update_id, attempts=first["attempts"])
        inbox.mark_processed(update_id, attempts=second["attempts"])
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_encrypted_retry_retains_ciphertext_then_clears_terminal_row():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    marker = "retry-envelope-marker"
    payload = {"update_id": update_id, "message": {"text": marker}}
    _apply_migrations(DSN)
    inbox = _inbox()
    try:
        assert inbox.accept_encrypted(update_id, payload)
        first = inbox.claim_next()
        assert first is not None
        inbox.retry_or_dead_letter(
            update_id, attempts=first["attempts"], error_code="SyntheticFailure"
        )
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                """SELECT status, payload, encrypted_payload, payload_expires_at, last_error_code
                   FROM public.telegram_update_inbox WHERE update_id = %s""",
                (update_id,),
            ).fetchone()
        assert row[0] == "pending"
        assert row[1] is None
        assert row[2] is not None
        assert marker.encode() not in bytes(row[2])
        assert row[3] is not None
        assert row[4] == "SyntheticFailure"

        with psycopg.connect(DSN) as conn:
            conn.execute(
                "UPDATE public.telegram_update_inbox SET available_at = now() - interval '1 second' "
                "WHERE update_id = %s",
                (update_id,),
            )
        retry = inbox.claim_next()
        assert retry is not None
        assert retry["attempts"] == first["attempts"] + 1
        assert retry["payload"] == payload
        inbox.retry_or_dead_letter(
            update_id,
            attempts=retry["attempts"],
            error_code="TerminalFailure",
            max_attempts=retry["attempts"],
        )
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                """SELECT status, payload, encrypted_payload, payload_expires_at
                   FROM public.telegram_update_inbox WHERE update_id = %s""",
                (update_id,),
            ).fetchone()
        assert row == ("dead_letter", None, None, None)
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_legacy_payloads_are_encrypted_before_worker_dispatch():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    marker = "legacy-plaintext-migration-marker"
    payload = {"update_id": update_id, "message": {"text": marker}}
    _apply_migrations(DSN)
    inbox = _inbox()
    try:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                """INSERT INTO public.telegram_update_inbox (update_id, payload)
                   VALUES (%s, %s::jsonb)""",
                (update_id, json.dumps(payload, separators=(",", ":"), ensure_ascii=False)),
            )
        assert inbox.secure_legacy_payloads() == 1
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                """SELECT payload, encrypted_payload, payload_expires_at
                   FROM public.telegram_update_inbox WHERE update_id = %s""",
                (update_id,),
            ).fetchone()
        assert row[0] is None
        assert row[1] is not None
        assert marker.encode() not in bytes(row[1])
        assert row[2] is not None

        claimed = inbox.claim_next()
        assert claimed is not None
        assert claimed["update_id"] == update_id
        assert claimed["payload"] == payload
        inbox.mark_processed(update_id, attempts=claimed["attempts"])
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_expired_encrypted_payload_is_dead_lettered_and_cleared():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    payload = {"update_id": update_id, "message": {"text": "expires"}}
    _apply_migrations(DSN)
    inbox = _inbox()
    try:
        assert inbox.accept_encrypted(update_id, payload)
        with psycopg.connect(DSN) as conn:
            conn.execute(
                """UPDATE public.telegram_update_inbox
                   SET payload_expires_at = now() - interval '1 second'
                   WHERE update_id = %s""",
                (update_id,),
            )
        assert inbox.claim_next() is None
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                """SELECT status, payload, encrypted_payload, payload_expires_at, last_error_code
                   FROM public.telegram_update_inbox WHERE update_id = %s""",
                (update_id,),
            ).fetchone()
        assert row == ("dead_letter", None, None, None, "payload_expired")
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )

def test_encrypted_enqueue_fails_closed_without_an_encryption_key():
    inbox = PostgresTelegramInbox(
        connection_factory=lambda: pytest.fail("database must not be reached without a key"),
        encryption_keys=[],
    )

    with pytest.raises(RuntimeError, match="ENCRYPTION_KEYS is required"):
        inbox.accept_encrypted(123, {"update_id": 123, "message": {"text": "synthetic"}})


def test_encrypted_enqueue_rejects_invalid_encryption_key():
    with pytest.raises(ValueError, match="valid Fernet keys"):
        PostgresTelegramInbox(
            connection_factory=lambda: pytest.fail("database must not be reached with an invalid key"),
            encryption_keys=["not-a-fernet-key"],
        )

