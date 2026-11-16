import asyncio
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.web.telegram_webhook_app import MAX_WEBHOOK_BODY_BYTES, create_webhook_app


class FakeInbox:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.ids: set[int] = set()
        self.accepted: list[tuple[int, dict]] = []

    def accept_encrypted(self, update_id: int, payload: dict) -> bool:
        if self.fail:
            raise OSError("database unavailable")
        if update_id in self.ids:
            return False
        self.ids.add(update_id)
        self.accepted.append((update_id, payload))
        return True


def _payload(update_id: int = 123) -> dict:
    return {
        "update_id": update_id,
        "message": {
            "message_id": 1,
            "date": 1700000000,
            "chat": {"id": 987, "type": "private"},
            "from": {"id": 987, "is_bot": False, "first_name": "Synthetic"},
            "text": "/start",
        },
    }


def _client(monkeypatch, inbox: FakeInbox | None):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "test-secret")
    application = MagicMock()
    application.bot = MagicMock()
    monkeypatch.setattr(
        "src.web.telegram_webhook_app.Update.de_json",
        lambda payload, bot: SimpleNamespace(update_id=payload["update_id"]),
    )
    return TestClient(create_webhook_app(application=application, inbox=inbox))


def _headers(secret: str = "test-secret") -> dict[str, str]:
    return {"X-Telegram-Bot-Api-Secret-Token": secret}


def test_webhook_rejects_missing_or_invalid_secret(monkeypatch):
    client = _client(monkeypatch, FakeInbox())
    assert client.post("/telegram/webhook", json=_payload()).status_code == 403
    assert client.post(
        "/telegram/webhook", json=_payload(), headers=_headers("wrong-secret")
    ).status_code == 403


def test_webhook_acknowledges_only_after_durable_acceptance(monkeypatch):
    inbox = FakeInbox()
    response = _client(monkeypatch, inbox).post(
        "/telegram/webhook", json=_payload(), headers=_headers()
    )

    assert response.status_code == 202
    assert inbox.accepted == [(123, _payload())]


def test_duplicate_update_is_acknowledged_without_duplicate_acceptance(monkeypatch):
    inbox = FakeInbox()
    client = _client(monkeypatch, inbox)

    assert client.post("/telegram/webhook", json=_payload(), headers=_headers()).status_code == 202
    assert client.post("/telegram/webhook", json=_payload(), headers=_headers()).status_code == 202
    assert len(inbox.accepted) == 1


def test_inbox_failure_returns_retryable_503(monkeypatch):
    response = _client(monkeypatch, FakeInbox(fail=True)).post(
        "/telegram/webhook", json=_payload(), headers=_headers()
    )
    assert response.status_code == 503


def test_missing_durable_inbox_returns_retryable_503(monkeypatch):
    response = _client(monkeypatch, None).post(
        "/telegram/webhook", json=_payload(), headers=_headers()
    )
    assert response.status_code == 503
    assert "durable inbox is unavailable" in response.json()["detail"]


def test_webhook_rejects_malformed_and_non_object_json(monkeypatch):
    client = _client(monkeypatch, FakeInbox())
    malformed = client.post("/telegram/webhook", content=b'{"update_id":', headers=_headers())
    non_object = client.post("/telegram/webhook", json=["not", "an", "update"], headers=_headers())

    assert malformed.status_code == 400
    assert non_object.status_code == 400


def test_webhook_rejects_oversized_body(monkeypatch):
    client = _client(monkeypatch, FakeInbox())
    response = client.post(
        "/telegram/webhook",
        content=b"x" * (MAX_WEBHOOK_BODY_BYTES + 1),
        headers=_headers(),
    )
    assert response.status_code == 413


def test_liveness_route_is_available():
    client = TestClient(create_webhook_app(application=MagicMock()))
    response = client.get("/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "surface": "telegram-webhook"}


def test_standalone_telegram_entry_point_fails_closed():
    from src.bot_telegram import main

    with pytest.raises(RuntimeError, match="Telegram polling is disabled"):
        main()


def test_render_manifest_declares_webhook_and_not_polling():
    source = Path(__file__).resolve().parents[1] / "render.yaml"
    manifest = source.read_text(encoding="utf-8")

    assert "src.web.telegram_webhook_app:app" in manifest
    assert "python src/bot_telegram.py" not in manifest


def test_start_discloses_telegram_data_boundary():
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from src.commands.start import start

    reply = AsyncMock()
    update = SimpleNamespace(message=SimpleNamespace(reply_text=reply))
    asyncio.run(start(update, MagicMock()))

    message = " ".join(reply.await_args.args[0].split())
    assert "not an end-to-end encrypted Secret Chat" in message
    assert "processed by Telegram and Janavani's bot service" in message
    assert "Please do not send identity documents" in message

def test_inbox_worker_shutdown_does_not_mask_worker_failure(caplog):
    import asyncio

    from src.web.telegram_webhook_app import _stop_inbox_worker

    async def failed_worker():
        raise RuntimeError("synthetic database outage with sensitive detail")

    async def exercise_shutdown():
        worker = asyncio.create_task(failed_worker())
        await asyncio.sleep(0)
        await _stop_inbox_worker(worker)

    asyncio.run(exercise_shutdown())

    assert "Telegram inbox shutdown worker failure type=RuntimeError" in caplog.text
    assert "sensitive detail" not in caplog.text



class RetryingStartupInbox(FakeInbox):
    def __init__(self) -> None:
        super().__init__()
        self.migration_attempts = 0
        self.first_attempt = threading.Event()

    def secure_legacy_payloads(self) -> int:
        self.migration_attempts += 1
        self.first_attempt.set()
        if self.migration_attempts == 1:
            raise OSError("synthetic database DNS outage")
        return 0


def test_production_startup_retries_database_and_keeps_ingress_unready(monkeypatch):
    from src.web import telegram_webhook_app as webhook_module
    from src.web import telegram_webhook_lifecycle as lifecycle_module

    inbox = RetryingStartupInbox()
    application = MagicMock()
    application.initialize = AsyncMock()
    application.start = AsyncMock()
    application.stop = AsyncMock()
    application.shutdown = AsyncMock()
    application.bot.set_my_commands = AsyncMock()
    application.bot.set_webhook = AsyncMock()
    settings = SimpleNamespace(
        bot_token="synthetic-token",
        webhook_url="https://example.test/telegram/webhook",
        secret="test-secret",
        inbox_dsn="postgresql://synthetic",
        encryption_keys=("x" * 32,),
    )

    async def idle_worker(*_args):
        await asyncio.Future()

    monkeypatch.setattr(webhook_module, "load_telegram_webhook_settings", lambda: settings)
    monkeypatch.setattr(webhook_module, "build_application", lambda **_kwargs: application)
    monkeypatch.setattr(webhook_module, "PostgresTelegramInbox", lambda **_kwargs: inbox)
    monkeypatch.setattr(
        webhook_module.Update,
        "de_json",
        lambda payload, _bot: SimpleNamespace(update_id=payload["update_id"]),
    )
    monkeypatch.setattr(lifecycle_module, "run_inbox_worker", idle_worker)
    monkeypatch.setattr(lifecycle_module, "_start_ephemeral_issue_cleanup", lambda _app: None)
    monkeypatch.setattr(
        lifecycle_module, "_stop_ephemeral_issue_cleanup", AsyncMock()
    )
    monkeypatch.setattr(lifecycle_module, "STARTUP_RETRY_INITIAL_SECONDS", 0.05)
    monkeypatch.setattr(lifecycle_module, "STARTUP_RETRY_MAX_SECONDS", 0.05)

    app = webhook_module.create_webhook_app()
    with TestClient(app) as client:
        assert inbox.first_attempt.wait(2)
        assert client.get("/liveness").status_code == 200
        assert client.get("/readiness").status_code == 503
        rejected = client.post(
            "/telegram/webhook", json=_payload(), headers=_headers()
        )
        assert rejected.status_code == 503

        deadline = time.monotonic() + 3
        while not app.state.runtime_ready and time.monotonic() < deadline:
            time.sleep(0.01)

        assert app.state.runtime_ready is True
        assert client.get("/readiness").status_code == 200
        assert inbox.migration_attempts == 2
        assert application.initialize.await_count == 1
        assert application.start.await_count == 1
        application.bot.set_webhook.assert_awaited_once()

        accepted = client.post(
            "/telegram/webhook", json=_payload(), headers=_headers()
        )
        assert accepted.status_code == 202
        assert inbox.accepted == [(123, _payload())]

    assert application.stop.await_count == 1
    assert application.shutdown.await_count == 1


def test_unexpected_inbox_worker_exit_marks_runtime_unready(caplog):
    from types import SimpleNamespace

    from src.web.telegram_webhook_lifecycle import watch_worker_exit

    app = SimpleNamespace(state=SimpleNamespace(runtime_ready=True))

    async def failed_worker():
        raise OSError("synthetic database failure with sensitive connection details")

    async def exercise():
        worker = asyncio.create_task(failed_worker())
        watch_worker_exit(app, worker)
        await worker

    asyncio.run(exercise())

    assert app.state.runtime_ready is False
    assert "Telegram inbox worker exited unexpectedly reason=OSError" in caplog.text
    assert "sensitive connection details" not in caplog.text
