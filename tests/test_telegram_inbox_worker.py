import asyncio
import threading
from types import SimpleNamespace

import pytest

from src.web import telegram_inbox_worker


async def _wait_for_event(event: threading.Event, timeout: float) -> bool:
    """Wait without occupying an executor thread during worker shutdown."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while not event.is_set():
        remaining = deadline - loop.time()
        if remaining <= 0:
            return False
        await asyncio.sleep(min(0.01, remaining))
    return True


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
            assert await _wait_for_event(inbox.retried, 2), "worker did not retry failed handler"
        finally:
            worker.cancel()
            try:
                await asyncio.wait_for(worker, timeout=1)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                pytest.fail("worker did not stop within 1s after cancellation")

    asyncio.run(run_until_retry())
    assert inbox.retried.is_set()
    assert not inbox.processed
    assert not hasattr(application, "error_handler")


def test_worker_cancels_dispatch_when_lease_renewal_fails(monkeypatch):
    class BlockingApplication(_Application):
        async def process_update(self, update):
            await asyncio.Event().wait()

    # Force lease loss deterministically while the handler is still awaiting work.
    async def lease_fails_immediately(inbox, update_id, attempts):
        raise RuntimeError("lease lost")

    monkeypatch.setattr(telegram_inbox_worker, "_renew_lease", lease_fails_immediately)

    monkeypatch.setattr(
        telegram_inbox_worker.Update, "de_json",
        lambda payload, bot: SimpleNamespace(update_id=payload["update_id"]),
    )
    inbox, application = _Inbox(), BlockingApplication()

    async def run_until_retry():
        worker = asyncio.create_task(
            telegram_inbox_worker.run_inbox_worker(application, inbox, poll_seconds=0.01)
        )
        try:
            assert await _wait_for_event(inbox.retried, 2), (
                "worker did not retry after lease loss"
            )
        finally:
            worker.cancel()
            try:
                await asyncio.wait_for(worker, timeout=1)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                pytest.fail("worker did not stop within 1s after cancellation")

    asyncio.run(run_until_retry())
    assert inbox.retried.is_set()
    assert not inbox.processed
    assert not hasattr(application, "error_handler")



class _RecoveringInbox:
    """Raise one transient claim error, then return one update and complete it."""

    def __init__(self):
        self.claims = 0
        self.processed = threading.Event()

    def claim_next(self):
        self.claims += 1
        if self.claims == 1:
            raise TimeoutError("synthetic database connection timeout")
        if self.claims == 2:
            return {"update_id": 45, "payload": {"update_id": 45}, "attempts": 1}
        return None

    def heartbeat(self, update_id, *, attempts):
        return None

    def retry_or_dead_letter(self, update_id, *, attempts, error_code):
        raise AssertionError("successful recovery must not retry a business update")

    def mark_processed(self, update_id, *, attempts):
        self.processed.set()


class _SuccessfulApplication(_Application):
    async def process_update(self, update):
        return None


def test_worker_survives_transient_database_error_while_claiming(monkeypatch):
    monkeypatch.setattr(
        telegram_inbox_worker.Update, "de_json",
        lambda payload, bot: SimpleNamespace(update_id=payload["update_id"]),
    )
    inbox, application = _RecoveringInbox(), _SuccessfulApplication()

    async def run_until_processed():
        worker = asyncio.create_task(
            telegram_inbox_worker.run_inbox_worker(application, inbox, poll_seconds=0.01)
        )
        try:
            assert await _wait_for_event(inbox.processed, 3), (
                "worker terminated instead of retrying after a transient claim failure"
            )
        finally:
            worker.cancel()
            try:
                await asyncio.wait_for(worker, timeout=1)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                pytest.fail("worker did not stop within 1s after cancellation")

    asyncio.run(run_until_processed())
    assert inbox.claims >= 2
    assert inbox.processed.is_set()
    assert not hasattr(application, "error_handler")
