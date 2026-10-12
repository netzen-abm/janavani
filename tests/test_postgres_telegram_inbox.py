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
    assert inbox.accept(update_id, payload) is True
    assert inbox.accept(update_id, payload) is False
    item = inbox.claim_next()
    assert item is not None
    assert item["update_id"] == update_id
    assert item["payload"]["test_marker"] == "inbox-contract"
    inbox.mark_processed(update_id)
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            "SELECT status, payload FROM public.telegram_update_inbox WHERE update_id = %s",
            (update_id,),
        ).fetchone()
    assert row == ("processed", None)
