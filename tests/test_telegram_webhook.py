from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from telegram.ext import Defaults

from src.web.telegram_webhook_app import create_webhook_app


def _application():
    application = MagicMock()
    application.bot = MagicMock()
    application.bot.defaults = Defaults()
    application.update_queue = MagicMock()
    application.update_queue.put = AsyncMock()
    return application


def _payload():
    return {
        "update_id": 123,
        "message": {
            "message_id": 1,
            "date": 1700000000,
            "chat": {"id": 987, "type": "private"},
            "from": {"id": 987, "is_bot": False, "first_name": "Test"},
            "text": "/start",
        },
    }


def _post(client, *, content=None, json=None, secret="test-secret"):
    headers = {"X-Telegram-Bot-Api-Secret-Token": secret}
    if json is not None:
        return client.post("/telegram/webhook", json=json, headers=headers)
    return client.post("/telegram/webhook", content=content, headers=headers)


def test_webhook_rejects_missing_or_wrong_secret():
    client = TestClient(create_webhook_app(application=_application()))
    response = client.post("/telegram/webhook", json={"update_id": 1})
    assert response.status_code == 403

    response = client.post(
        "/telegram/webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
    )
    assert response.status_code == 403


def test_webhook_accepts_valid_secret_and_queues_update():
    application = _application()
    client = TestClient(create_webhook_app(application=application))
    response = _post(client, json=_payload())

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    application.update_queue.put.assert_awaited_once()


def test_webhook_returns_retryable_status_if_queue_rejects_update():
    application = _application()
    application.update_queue.put.side_effect = RuntimeError("queue unavailable")
    client = TestClient(create_webhook_app(application=application))

    response = _post(client, json=_payload())

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Telegram update could not be accepted; retry delivery"
    )


def test_webhook_rejects_malformed_json_without_queueing():
    application = _application()
    client = TestClient(create_webhook_app(application=application))

    response = _post(client, content=b'{"update_id":')

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON update"
    application.update_queue.put.assert_not_awaited()


def test_webhook_rejects_non_object_json_without_queueing():
    application = _application()
    client = TestClient(create_webhook_app(application=application))

    response = _post(client, json=["not", "an", "update"])

    assert response.status_code == 400
    assert response.json()["detail"] == "Update must be a JSON object"
    application.update_queue.put.assert_not_awaited()


def test_webhook_rejects_update_parser_exception_without_queueing(monkeypatch):
    application = _application()
    client = TestClient(create_webhook_app(application=application))

    def raise_parser_error(payload, bot):
        raise TypeError("unexpected update field")

    monkeypatch.setattr("src.web.telegram_webhook_app.Update.de_json", raise_parser_error)
    response = _post(client, json=_payload())

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Telegram update"
    application.update_queue.put.assert_not_awaited()


def test_webhook_liveness_is_available():
    client = TestClient(create_webhook_app(application=_application()))
    response = client.get("/liveness")
    assert response.status_code == 200
    assert response.json() == {
        "status": "alive",
        "surface": "telegram-webhook",
    }



def test_render_webhook_runtime_exposes_src_import_path():
    from pathlib import Path

    render_config = (Path(__file__).resolve().parents[1] / "render.yaml").read_text(
        encoding="utf-8"
    )
    assert (
        "startCommand: PYTHONPATH=src uvicorn src.web.telegram_webhook_app:app "
        "--host 0.0.0.0 --port $PORT"
    ) in render_config


def test_webhook_registers_the_shared_command_catalogue(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    import src.web.telegram_webhook_app as webhook
    from src.commands.catalogue import telegram_bot_commands

    bot = SimpleNamespace(
        set_my_commands=AsyncMock(),
        set_webhook=AsyncMock(),
    )
    application = SimpleNamespace(
        bot=bot,
        bot_data={},
        initialize=AsyncMock(),
        start=AsyncMock(),
        stop=AsyncMock(),
        shutdown=AsyncMock(),
        add_error_handler=MagicMock(),
        remove_error_handler=MagicMock(),
    )

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL", "https://bot.example/telegram/webhook")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "janavani-webhook-test-secret-123456789")
    monkeypatch.setenv("JANAVANI_TELEGRAM_INBOX_DSN", "postgresql://test-only")
    monkeypatch.setattr(webhook, "build_application", lambda *, token: application)
    monkeypatch.setattr(
        webhook,
        "PostgresTelegramInbox",
        lambda *, dsn: SimpleNamespace(dsn=dsn),
    )

    async def idle_worker(_application, _inbox):
        await asyncio.Event().wait()

    monkeypatch.setattr(webhook, "run_inbox_worker", idle_worker)

    cleanup_task = None
    with TestClient(webhook.create_webhook_app()) as client:
        assert client.get("/liveness").status_code == 200
        bot.set_my_commands.assert_awaited_once_with(telegram_bot_commands())
        names = [item.command for item in bot.set_my_commands.await_args.args[0]]
        assert "cases" in names
        assert len(names) == len(set(names))
        cleanup_task = application.bot_data.get("janavani_ephemeral_issue_cleanup")
        assert cleanup_task is not None and not cleanup_task.done()

    assert cleanup_task.cancelled()
    assert application.bot_data.get("janavani_ephemeral_issue_cleanup") is None
    application.stop.assert_awaited_once()
    application.shutdown.assert_awaited_once()

class _ReceiptOnlyInbox:
    """Test receipt state without an API that accepts or persists raw payloads."""

    def __init__(self):
        self.status = "claimed"
        self.claimed_ids = []
        self.processed = []
        self.retried = []
        self.legacy_payload_accepts = 0

    def claim_update(self, update_id):
        self.claimed_ids.append(update_id)
        return {"status": self.status, "attempts": 1}

    def heartbeat(self, update_id, *, attempts):
        return None

    def mark_processed(self, update_id, *, attempts):
        self.processed.append((update_id, attempts))
        self.status = "processed"

    def retry_or_dead_letter(self, update_id, *, attempts, error_code):
        self.retried.append((update_id, attempts, error_code))
        self.status = "pending"

    def claim_next(self):
        # The compatibility worker must have no new payload-bearing rows to claim.
        return None

    def accept_legacy_payload(self, update_id, payload):
        self.legacy_payload_accepts += 1
        raise AssertionError("New webhook updates must not enqueue raw payloads")


def test_durable_webhook_processes_inline_and_stores_only_receipt_state():
    application = _application()
    application.process_update = AsyncMock()
    inbox = _ReceiptOnlyInbox()
    client_app = create_webhook_app(application=application, inbox=inbox)

    with TestClient(client_app) as client:
        response = _post(client, json=_payload())

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    assert inbox.claimed_ids == [123]
    assert inbox.processed == [(123, 1)]
    assert inbox.retried == []
    assert inbox.legacy_payload_accepts == 0
    application.process_update.assert_awaited_once()
    application.update_queue.put.assert_not_awaited()


def test_durable_webhook_returns_retryable_failure_when_handler_raises():
    application = _application()
    application.process_update = AsyncMock(side_effect=RuntimeError("synthetic failure"))
    inbox = _ReceiptOnlyInbox()
    client_app = create_webhook_app(application=application, inbox=inbox)

    with TestClient(client_app) as client:
        response = _post(client, json=_payload())

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Telegram update could not be completed; retry delivery"
    )
    assert inbox.claimed_ids == [123]
    assert inbox.processed == []
    assert inbox.retried == [(123, 1, "RuntimeError")]
    assert inbox.legacy_payload_accepts == 0


def test_durable_webhook_returns_retryable_failure_when_ptb_reports_handler_error():
    from types import SimpleNamespace

    application = _application()
    inbox = _ReceiptOnlyInbox()
    client_app = create_webhook_app(application=application, inbox=inbox)

    async def report_error(update):
        registered = application.add_error_handler.call_args_list
        inline_handler = registered[0].args[0]
        await inline_handler(update, SimpleNamespace(error=RuntimeError("handler failed")))

    application.process_update = AsyncMock(side_effect=report_error)

    with TestClient(client_app) as client:
        response = _post(client, json=_payload())

    assert response.status_code == 503
    assert inbox.processed == []
    assert inbox.retried == [(123, 1, "RuntimeError")]

