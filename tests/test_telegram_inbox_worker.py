"""Focused reliability tests for the internal Telegram webhook inbox worker."""
from __future__ import annotations

import asyncio
import threading
import time
from types import SimpleNamespace

from src.web.telegram_inbox_worker import run_inbox_worker


class TransientOutageInbox:
    def __init__(self, update_id: int, payload: dict):
        self.update_id = update_id
        self.payload = payload
        self.claim_calls = 0
        self.processed: list[tuple[int, int]] = []
        self.retry_calls: list[tuple[int, int, str]] = []
        self.done = threading.Event()

    def claim_next(self):
        self.claim_calls += 1
        if self.claim_calls == 1:
            raise OSError("synthetic database outage")
        if self.claim_calls == 2:
            return {
                "update_id": self.update_id,
                "payload": self.payload,
                "attempts": 1,
            }
        return None

    def mark_processed(self, update_id: int, *, attempts: int):
        self.processed.append((update_id, attempts))
        self.done.set()

    def heartbeat(self, update_id: int, *, attempts: int):
        return None

    def retry_or_dead_letter(
        self, update_id: int, *, attempts: int, error_code: str, max_attempts: int = 8
    ):
        self.retry_calls.append((update_id, attempts, error_code))


class ApplicationHarness:
    bot = None

    def __init__(self):
        self.bot_data = {}
        self.processed_updates: list[int] = []
        self._error_handlers = []

    def add_error_handler(self, handler):
        self._error_handlers.append(handler)

    def remove_error_handler(self, handler):
        self._error_handlers.remove(handler)

    async def process_update(self, update):
        self.processed_updates.append(update.update_id)


def test_webhook_inbox_worker_recovers_from_transient_database_outage_without_duplicate_dispatch():
    update_id = time.time_ns() % 9_000_000_000_000_000
    user_id = 700_000_000 + update_id % 100_000_000
    payload = {
        "update_id": update_id,
        "message": {
            "message_id": 1,
            "date": int(time.time()),
            "chat": {"id": user_id, "type": "private", "first_name": "Synthetic"},
            "from": {"id": user_id, "is_bot": False, "first_name": "Synthetic"},
            "text": "/start",
        },
    }
    inbox = TransientOutageInbox(update_id, payload)
    application = ApplicationHarness()

    async def run_worker_until_processed():
        worker = asyncio.create_task(
            run_inbox_worker(application, inbox, poll_seconds=0.01)
        )
        try:
            completed = await asyncio.to_thread(inbox.done.wait, 5)
            assert completed, "worker did not recover and acknowledge the synthetic update"
            await asyncio.sleep(0.05)
        finally:
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass

    asyncio.run(run_worker_until_processed())

    assert inbox.claim_calls >= 3, "worker did not retry after its transient database outage"
    assert application.processed_updates == [update_id]
    assert inbox.processed == [(update_id, 1)]
    assert inbox.retry_calls == []
    assert application._error_handlers == []
