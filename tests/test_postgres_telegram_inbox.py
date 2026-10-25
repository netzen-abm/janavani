import os
import time
from pathlib import Path

import pytest

from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
MIGRATIONS = (
    ROOT / "db/migrations/20261012120000_telegram_update_inbox.sql",
    ROOT / "db/migrations/20261025120000_telegram_inbox_content_free_receipts.sql",
)


def _apply_migrations(dsn: str) -> None:
    import psycopg

    with psycopg.connect(dsn) as conn:
        for migration_path in MIGRATIONS:
            conn.execute(migration_path.read_text(encoding="utf-8"))


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_telegram_inbox_accept_claim_complete_and_deduplicate():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    payload = {"update_id": update_id, "test_marker": "inbox-contract"}
    _apply_migrations(DSN)
    inbox = PostgresTelegramInbox(dsn=DSN)
    try:
        assert inbox.accept_legacy_payload(update_id, payload) is True
        assert inbox.accept_legacy_payload(update_id, payload) is False
        first = inbox.claim_next()
        assert first is not None and first["update_id"] == update_id
        assert first["payload"]["test_marker"] == "inbox-contract"
        second = inbox.claim_next()
        assert second is None
        inbox.mark_processed(update_id, attempts=first["attempts"])
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                "SELECT status, payload FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert row == ("processed", None)
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_telegram_inbox_fences_a_reclaimed_worker():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    _apply_migrations(DSN)
    inbox = PostgresTelegramInbox(dsn=DSN)
    try:
        assert inbox.accept_legacy_payload(update_id, {"update_id": update_id})
        first = inbox.claim_next()
        assert first is not None and first["update_id"] == update_id
        with psycopg.connect(DSN) as conn:
            conn.execute(
                """UPDATE public.telegram_update_inbox SET locked_at = now() - interval '5 minutes'
                   WHERE update_id = %s""",
                (update_id,),
            )
        second = inbox.claim_next(stale_after_seconds=1)
        assert second is not None and second["update_id"] == update_id
        assert second["attempts"] == first["attempts"] + 1
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
def test_postgres_inline_webhook_receipt_never_persists_raw_payload():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    _apply_migrations(DSN)
    inbox = PostgresTelegramInbox(dsn=DSN)
    try:
        first = inbox.claim_update(update_id)
        assert first == {"status": "claimed", "attempts": 1}

        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                "SELECT status, payload FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert row == ("processing", None)

        duplicate_while_processing = inbox.claim_update(update_id)
        assert duplicate_while_processing["status"] == "busy"

        inbox.mark_processed(update_id, attempts=first["attempts"])
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                "SELECT status, payload FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert row == ("processed", None)
        assert inbox.claim_update(update_id)["status"] == "processed"
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_inline_receipt_reclaims_stale_claim_without_payload():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    _apply_migrations(DSN)
    inbox = PostgresTelegramInbox(dsn=DSN)
    try:
        first = inbox.claim_update(update_id)
        assert first["status"] == "claimed"
        with psycopg.connect(DSN) as conn:
            conn.execute(
                """UPDATE public.telegram_update_inbox
                   SET locked_at = now() - interval '5 minutes'
                   WHERE update_id = %s""",
                (update_id,),
            )
        second = inbox.claim_update(update_id, stale_after_seconds=1)
        assert second["status"] == "claimed"
        assert second["attempts"] == first["attempts"] + 1
        with psycopg.connect(DSN) as conn:
            row = conn.execute(
                "SELECT status, payload FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert row == ("processing", None)
        with pytest.raises(RuntimeError, match="not owned"):
            inbox.mark_processed(update_id, attempts=first["attempts"])
        inbox.mark_processed(update_id, attempts=second["attempts"])
    finally:
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,)
            )

