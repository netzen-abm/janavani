"""PostgreSQL proof that replay after a Telegram handler commit is safe."""
from __future__ import annotations
import asyncio, os, threading, time
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
import pytest
from telegram import Message
from conversation.constants import WAITING_FOR_OFFICE_SELECTION
from conversation.engine import run_step
from conversation.session import clear_session, get_session, set_ephemeral_issue
from conversation.state import set_state, user_states
from src.adapters.telegram.identity import identity_for_telegram_user
from src.identity.pairing import IdentityPairingService
from src.identity.linking import PostgresExternalIdentityLinkRepository
from src.platform.surface_case_composition import create_surface_case_composition
from src.storage.repositories.postgres_civic_case import PostgresCivicCaseRepository
from src.storage.repositories.postgres_identity_pairing import PostgresPairingRepository
from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox
from src.web.telegram_inbox_worker import run_inbox_worker
ROOT = Path(__file__).resolve().parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN")
FERNET_KEY = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
MIGRATIONS = (
    "db/migrations/20260912100000_canonical_case_policy_schema.sql",
    "db/migrations/20260920100000_external_identity_links.sql",
    "db/migrations/20261010120000_external_identity_pairings.sql",
    "db/migrations/20261012120000_telegram_update_inbox.sql",
    "db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql",
)
class SimulatedWorkerCrash(BaseException):
    pass
class ApplicationHarness:
    """Use the actual state dispatcher without making external Bot API calls."""
    bot = None
    def __init__(self, bot_data):
        self.bot_data, self.error_handler = bot_data, None
    def add_error_handler(self, handler):
        self.error_handler = handler
    def remove_error_handler(self, handler):
        assert handler is self.error_handler
        self.error_handler = None
    async def process_update(self, update):
        await run_step(update, SimpleNamespace(application=self))
@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_telegram_case_handler_post_commit_crash_replay_is_safe(monkeypatch):
    """A fresh worker must not create a second Case after process-local state is lost."""
    import psycopg
    runtime_dsns = {os.getenv(k, "").strip() for k in (
        "JANAVANI_POSTGRES_DSN", "JANAVANI_IDENTITY_LINKS_DSN", "JANAVANI_CASE_DATABASE_URL"
    )} - {""}
    assert DSN not in runtime_dsns, "integration DSN must not be a runtime database"
    assert any(x in DSN.lower() for x in ("test", "localhost", "127.0.0.1"))
    assert os.getenv("JANAVANI_RUNTIME_MODE", "test").lower() != "production"
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "test")
    monkeypatch.setenv("JANAVANI_CASE_CONTENT_POLICY", "transient")
    user_id = 700_000_000 + int(uuid4().hex[:7], 16)
    principal_id, telegram_subject = f"replay-citizen-{uuid4().hex}", str(user_id)
    update_id, pairing_id, case_id = time.time_ns() % 9_000_000_000_000_000, None, None
    replies = []
    async def fake_reply_text(_message, text, *args, **kwargs):
        replies.append(str(text))
    monkeypatch.setattr(Message, "reply_text", fake_reply_text)
    with psycopg.connect(DSN) as conn:
        for migration in MIGRATIONS:
            conn.execute((ROOT / migration).read_text(encoding="utf-8"))
    links = PostgresExternalIdentityLinkRepository(lambda: psycopg.connect(DSN))
    pairing = IdentityPairingService(PostgresPairingRepository(dsn=DSN))
    challenge = pairing.issue(principal_id=principal_id)
    pairing.claim_telegram(challenge.code, telegram_subject=telegram_subject)
    pairing.confirm_from_web(challenge.pairing_id, principal_id=principal_id, explicit_confirmation=True)
    pairing_id = challenge.pairing_id
    identity_for_telegram_user(user_id, links=links)
    composition = create_surface_case_composition(
        case_repository=PostgresCivicCaseRepository(dsn=DSN), identity_link_repository=links
    )
    class VerifiedAuthority:
        def require_verified_destination(self, authority_id: str):
            assert authority_id == "verified-office-test"
            return {"authority_id": authority_id}
    bot_data = {
        "case_repository": composition.case_repository,
        "civic_case_capability": composition.case_capability,
        "identity_link_repository": links,
        "authority_capability": VerifiedAuthority(),
    }
    payload = {"update_id": update_id, "message": {
        "message_id": 1, "date": int(time.time()),
        "chat": {"id": user_id, "type": "private", "first_name": "Synthetic"},
        "from": {"id": user_id, "is_bot": False, "first_name": "Synthetic"}, "text": "1",
    }}
    inbox = PostgresTelegramInbox(dsn=DSN, encryption_keys=[FERNET_KEY])
    try:
        assert inbox.accept_encrypted(update_id, payload)
        clear_session(user_id); user_states.pop(user_id, None)
        session = get_session(user_id)
        session.update(offices=[{"id": "verified-office-test", "name": "Synthetic Verified Office"}],
                       category="Streetlight outage", document="Complaint")
        set_ephemeral_issue(user_id, "Synthetic issue narrative for replay testing.")
        set_state(user_id, WAITING_FOR_OFFICE_SELECTION)
        def crash_before_ack(*args, **kwargs):
            raise SimulatedWorkerCrash("after Case commit, before inbox ack")
        inbox.mark_processed = crash_before_ack
        first_app = ApplicationHarness(bot_data)
        async def first_worker():
            await run_inbox_worker(first_app, inbox, poll_seconds=0.01)
        with pytest.raises(SimulatedWorkerCrash, match="before inbox ack"):
            asyncio.run(asyncio.wait_for(first_worker(), timeout=4))
        case_id = get_session(user_id)["case_id"]
        with psycopg.connect(DSN) as conn:
            case_row = conn.execute(
                "SELECT case_id, narrative, created_by FROM public.civic_cases WHERE case_id = %s",
                (case_id,),
            ).fetchone()
            event_count = conn.execute(
                "SELECT count(*) FROM public.civic_case_events WHERE case_id = %s", (case_id,)
            ).fetchone()[0]
            queued = conn.execute(
                "SELECT status, payload, encrypted_payload FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert case_row == (case_id, "", principal_id)
        assert event_count == 1 and queued[0] == "processing"
        assert queued[1] is None and queued[2] is not None
        # Simulate a new process: clear all workflow memory and expire the inbox lease.
        clear_session(user_id); user_states.pop(user_id, None)
        with psycopg.connect(DSN) as conn:
            conn.execute(
                "UPDATE public.telegram_update_inbox SET locked_at = now() - interval '5 minutes' WHERE update_id = %s",
                (update_id,),
            )
        fresh_inbox = PostgresTelegramInbox(dsn=DSN, encryption_keys=[FERNET_KEY])
        processed, original_mark = threading.Event(), None
        original_mark = fresh_inbox.mark_processed
        def mark_and_signal(*args, **kwargs):
            original_mark(*args, **kwargs); processed.set()
        fresh_inbox.mark_processed = mark_and_signal
        second_app = ApplicationHarness(bot_data)
        async def replay_worker():
            worker = asyncio.create_task(run_inbox_worker(second_app, fresh_inbox, poll_seconds=0.01))
            try:
                assert await asyncio.to_thread(processed.wait, 4), "replay was not acknowledged"
            finally:
                worker.cancel()
                try:
                    await worker
                except asyncio.CancelledError:
                    pass
        asyncio.run(replay_worker())
        with psycopg.connect(DSN) as conn:
            cases = conn.execute(
                "SELECT case_id FROM public.civic_cases WHERE created_by = %s", (principal_id,)
            ).fetchall()
            events = conn.execute(
                "SELECT event_id FROM public.civic_case_events WHERE case_id = %s", (case_id,)
            ).fetchall()
            queued = conn.execute(
                "SELECT status, payload, encrypted_payload, payload_expires_at FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert cases == [(case_id,)] and len(events) == 1
        assert queued == ("processed", None, None, None)
        assert any("describe the issue" in reply.lower() for reply in replies), replies
    finally:
        clear_session(user_id); user_states.pop(user_id, None)
        with psycopg.connect(DSN) as conn:
            conn.execute("DELETE FROM public.telegram_update_inbox WHERE update_id = %s", (update_id,))
            if case_id:
                conn.execute("DELETE FROM public.civic_case_events WHERE case_id = %s", (case_id,))
                conn.execute("DELETE FROM public.civic_cases WHERE case_id = %s", (case_id,))
            conn.execute(
                "DELETE FROM public.external_identity_links WHERE provider = 'telegram' AND subject = %s",
                (telegram_subject,),
            )
            if pairing_id:
                conn.execute("DELETE FROM public.external_identity_pairings WHERE pairing_id = %s", (pairing_id,))
