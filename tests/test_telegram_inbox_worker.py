import asyncio
import threading
from types import SimpleNamespace

import pytest

from src.web import telegram_inbox_worker


class _Inbox:
    def __init__(self):
        self.claims = 0
        self.retried = threading.Event()
        self.processed = False

    def claim_next(self):
        self.claims += 1
        if self.claims == 1:
            return {"update_id": 44, "payload": {"update_id": 44}, "attempts": 1}
        return None

    def heartbeat(self, update_id, *, attempts):
        return None

    def retry_or_dead_letter(self, update_id, *, attempts, error_code):
        self.retried.set()

    def mark_processed(self, update_id, *, attempts):
        self.processed = True


class _Application:
    bot = object()

    def add_error_handler(self, handler):
        self.error_handler = handler

    def remove_error_handler(self, handler):
        assert handler is self.error_handler
        del self.error_handler

    async def process_update(self, update):
        await self.error_handler(update, SimpleNamespace(error=RuntimeError("handler failed")))


def test_worker_retries_when_telegram_handler_reports_error(monkeypatch):
    monkeypatch.setattr(
        telegram_inbox_worker.Update, "de_json",
        lambda payload, bot: SimpleNamespace(update_id=payload["update_id"]),
    )
    inbox, application = _Inbox(), _Application()

    async def run_until_retry():
        worker = asyncio.create_task(
            telegram_inbox_worker.run_inbox_worker(application, inbox, poll_seconds=0.01)
        )
        try:
            assert await asyncio.to_thread(inbox.retried.wait, 2), "worker did not retry failed handler"
        finally:
            worker.cancel()
            with pytest.raises(asyncio.CancelledError):
                await worker

    asyncio.run(run_until_retry())
    assert inbox.retried.is_set()
    assert not inbox.processed
    assert not hasattr(application, "error_handler")
