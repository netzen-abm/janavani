"""PostgreSQL proof for safe Telegram inbox replay after a Case commit."""
from __future__ import annotations

import asyncio
import base64
import os
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from telegram import Message

from conversation.constants import WAITING_FOR_OFFICE_SELECTION
from conversation.engine import run_step
from conversation.session import clear_session, get_session, set_ephemeral_issue
from conversation.state import set_state, user_states
from src.capabilities.civic_case import CAPABILITY_ID
from src.identity.external import ExternalIdentity
from src.identity.linking import InMemoryExternalIdentityLinkRepository
from src.platform.surface_case_composition import create_surface_case_composition
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.postgres_civic_case import PostgresCivicCaseRepository
from src.storage.repositories.postgres_telegram_inbox import PostgresTelegramInbox
from src.web.telegram_inbox_worker import run_inbox_worker

ROOT = Path(__file__).parents[1]
DSN = os.getenv("JANAVANI_POSTGRES_TEST_DSN", "").strip()
FERNET_KEY = base64.urlsafe_b64encode(b"0" * 32).decode("ascii")
MIGRATIONS = (
    "db/migrations/20260912100000_canonical_case_policy_schema.sql",
    "db/migrations/20261012120000_telegram_update_inbox.sql",
    "db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql",
)


class SimulatedWorkerCrash(BaseException):
    """Simulate process loss after a Case transaction but before inbox acknowledgement."""


class ApplicationHarness:
    """Use the actual state dispatcher without making external Bot API calls."""

    bot = None

    def __init__(self, bot_data):
        self.bot_data = bot_data
        self._error_handler = None

    def add_error_handler(self, handler):
        self._error_handler = handler

    def remove_error_handler(self, handler):
        assert handler is self._error_handler
        self._error_handler = None

    async def process_update(self, update):
        await run_step(update, SimpleNamespace(application=self))


def _apply_migrations(dsn: str) -> None:
    import psycopg

    with psycopg.connect(dsn) as connection:
        for migration in MIGRATIONS:
            connection.execute((ROOT / migration).read_text(encoding="utf-8"))


@pytest.mark.integration
@pytest.mark.skipif(not DSN, reason="requires JANAVANI_POSTGRES_TEST_DSN")
def test_telegram_case_commit_replay_after_worker_restart_is_idempotent(monkeypatch):
    import psycopg

    runtime_dsns = {
        os.getenv(name, "").strip()
        for name in (
            "JANAVANI_POSTGRES_DSN",
            "JANAVANI_IDENTITY_LINKS_DSN",
            "JANAVANI_CASE_DATABASE_URL",
        )
    } - {""}
    assert DSN not in runtime_dsns, "integration DSN must not be a configured runtime database"
    assert any(token in DSN.lower() for token in ("test", "localhost", "127.0.0.1")), (
        "worker replay test requires a clearly identified disposable test database"
    )
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "test")
    monkeypatch.setenv("JANAVANI_CASE_CONTENT_POLICY", "transient")
    _apply_migrations(DSN)

    user_id = 700_000_000 + int(uuid4().hex[:7], 16)
    principal_id = f"synthetic-replay-principal-{uuid4().hex}"
    telegram_subject = str(user_id)
    update_id = time.time_ns() % 9_000_000_000_000_000
    replies: list[str] = []
    case_id = ""
    cleared_session = False

    async def fake_reply_text(_message, text, *args, **kwargs):
        replies.append(str(text))

    monkeypatch.setattr(Message, "reply_text", fake_reply_text)

    # Authorization is explicit test setup; the identity adapter itself must
    # not invent capabilities from a verified identity link.
    links = InMemoryExternalIdentityLinkRepository()
    links.save(
        ExternalIdentity(
            provider="telegram",
            subject=telegram_subject,
            principal_id=principal_id,
            authentication_method="explicit_verified_link",
            verified=True,
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )
    case_repository = PostgresCivicCaseRepository(dsn=DSN)
    composition = create_surface_case_composition(
        case_repository=case_repository,
        identity_link_repository=links,
        provider_composition=ProviderComposition.memory_first(),
    )

    class VerifiedAuthority:
        def require_verified_destination(self, authority_id: str):
            if authority_id != "verified-office-test":
                raise LookupError("authority is not verified")
            return {"authority_id": authority_id}

    application_data = {
        "case_repository": composition.case_repository,
        "civic_case_capability": composition.case_capability,
        "identity_link_repository": links,
        "authority_capability": VerifiedAuthority(),
    }
    payload = {
        "update_id": update_id,
        "message": {
            "message_id": 1,
            "date": int(time.time()),
            "chat": {"id": user_id, "type": "private", "first_name": "Synthetic"},
            "from": {"id": user_id, "is_bot": False, "first_name": "Synthetic"},
            "text": "1",
        },
    }
    inbox = PostgresTelegramInbox(dsn=DSN, encryption_keys=[FERNET_KEY])

    try:
        assert inbox.accept_encrypted(update_id, payload) is True
        clear_session(user_id)
        user_states.pop(user_id, None)
        session = get_session(user_id)
        session.update(
            offices=[{"id": "verified-office-test", "name": "Synthetic Verified Office"}],
            category="Streetlight outage",
            document="Complaint",
        )
        set_ephemeral_issue(user_id, "Synthetic issue narrative for replay testing.")
        set_state(user_id, WAITING_FOR_OFFICE_SELECTION)

        def crash_before_ack(_update_id, *, attempts):
            raise SimulatedWorkerCrash("synthetic crash after Case commit before inbox acknowledgement")

        inbox.mark_processed = crash_before_ack
        first_application = ApplicationHarness(application_data)

        with pytest.raises(SimulatedWorkerCrash, match="before inbox acknowledgement"):
            asyncio.run(
                asyncio.wait_for(
                    run_inbox_worker(first_application, inbox, poll_seconds=0.01),
                    timeout=5,
                )
            )

        case_id = str(get_session(user_id).get("case_id") or "")
        assert case_id, "the first worker must commit its Case before simulated process loss"
        with psycopg.connect(DSN) as connection:
            case_row = connection.execute(
                "SELECT case_id, narrative, created_by FROM public.civic_cases WHERE case_id = %s",
                (case_id,),
            ).fetchone()
            event_count = connection.execute(
                "SELECT count(*) FROM public.civic_case_events WHERE case_id = %s",
                (case_id,),
            ).fetchone()[0]
            inbox_row = connection.execute(
                "SELECT status, payload, encrypted_payload FROM public.telegram_update_inbox "
                "WHERE update_id = %s",
                (update_id,),
            ).fetchone()
        assert case_row == (case_id, "", principal_id)
        assert event_count == 1
        assert inbox_row[0] == "processing"
        assert inbox_row[1] is None and inbox_row[2] is not None

        # New process: all conversation memory is gone; the queue lease expires and
        # the same encrypted update becomes eligible for a fresh worker.
        clear_session(user_id)
        user_states.pop(user_id, None)
        cleared_session = True
        with psycopg.connect(DSN) as connection:
            connection.execute(
                "UPDATE public.telegram_update_inbox "
                "SET locked_at = now() - interval '5 minutes' WHERE update_id = %s",
                (update_id,),
            )

        fresh_inbox = PostgresTelegramInbox(dsn=DSN, encryption_keys=[FERNET_KEY])
        processed = threading.Event()
        original_mark_processed = fresh_inbox.mark_processed

        def mark_and_signal(replayed_update_id, *, attempts):
            original_mark_processed(replayed_update_id, attempts=attempts)
            processed.set()

        fresh_inbox.mark_processed = mark_and_signal
        second_application = ApplicationHarness(application_data)

        async def replay_worker():
            worker = asyncio.create_task(
                run_inbox_worker(second_application, fresh_inbox, poll_seconds=0.01)
            )
            try:
                acknowledged = await asyncio.to_thread(processed.wait, 5)
                assert acknowledged, "the restarted worker did not acknowledge the reclaimed update"
                await asyncio.sleep(0.05)
            finally:
                worker.cancel()
                try:
                    await worker
                except asyncio.CancelledError:
                    pass

        replies_before_replay = len(replies)
        asyncio.run(replay_worker())

        with psycopg.connect(DSN) as connection:
            cases = connection.execute(
                "SELECT case_id FROM public.civic_cases WHERE created_by = %s",
                (principal_id,),
            ).fetchall()
            replay_events = connection.execute(
                "SELECT event_id FROM public.civic_case_events WHERE case_id = %s",
                (case_id,),
            ).fetchall()
            terminal_inbox_row = connection.execute(
                "SELECT status, payload, encrypted_payload, payload_expires_at "
                "FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            ).fetchone()

        assert cases == [(case_id,)]
        assert len(replay_events) == 1
        assert terminal_inbox_row == ("processed", None, None, None)
        assert any("Welcome to Janavani" in text for text in replies[replies_before_replay:])

    finally:
        if not cleared_session:
            clear_session(user_id)
            user_states.pop(user_id, None)
        else:
            clear_session(user_id)
            user_states.pop(user_id, None)
        with psycopg.connect(DSN) as connection:
            if case_id:
                connection.execute("DELETE FROM public.civic_case_events WHERE case_id = %s", (case_id,))
                connection.execute("DELETE FROM public.civic_case_audit WHERE case_id = %s", (case_id,))
                connection.execute("DELETE FROM public.civic_cases WHERE case_id = %s", (case_id,))
            connection.execute(
                "DELETE FROM public.telegram_update_inbox WHERE update_id = %s",
                (update_id,),
            )
