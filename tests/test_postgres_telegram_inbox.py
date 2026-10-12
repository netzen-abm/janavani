import os
import time
from pathlib import Path

import pytest

from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
MIGRATION = (ROOT / "db/migrations/20261012120000_telegram_update_inbox.sql").read_text(
    encoding="utf-8"
)


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_postgres_telegram_inbox_accept_claim_complete_and_deduplicate():
    import psycopg

    update_id = time.time_ns() % 9_000_000_000_000_000
    payload = {"update_id": update_id, "test_marker": "inbox-contract"}
    with psycopg.connect(DSN) as conn:
        conn.execute(MIGRATION)
    inbox = PostgresTelegramInbox(dsn=DSN)
    try:
        assert inbox.accept(update_id, payload) is True
        assert inbox.accept(update_id, payload) is False
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
    with psycopg.connect(DSN) as conn:
        conn.execute(MIGRATION)
    inbox = PostgresTelegramInbox(dsn=DSN)
    try:
        assert inbox.accept(update_id, {"update_id": update_id})
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
