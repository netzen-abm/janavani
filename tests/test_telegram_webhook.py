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
    application.process_update = AsyncMock()
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
    import base64

    monkeypatch.setenv(
        "JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS",
        base64.urlsafe_b64encode(b"0" * 32).decode("ascii"),
    )
    monkeypatch.setattr(webhook, "build_application", lambda *, token: application)
    inbox = SimpleNamespace(
        dsn="postgresql://test-only",
        secure_legacy_payloads=MagicMock(return_value=0),
    )
    monkeypatch.setattr(
        webhook,
        "PostgresTelegramInbox",
        lambda *, dsn, encryption_keys: inbox,
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
    inbox.secure_legacy_payloads.assert_called_once_with()

class _EncryptedQueueInbox:
    """Test double for the durable encrypted-inbox API."""

    def __init__(self, *, fail=False):
        self.enqueued = {}
        self.fail = fail
        self.claim_next_calls = 0

    def accept_encrypted(self, update_id, payload):
        if self.fail:
            raise RuntimeError("synthetic secret narrative must not be logged")
        if update_id in self.enqueued:
            return False
        self.enqueued[update_id] = payload
        return True

    def claim_next(self):
        self.claim_next_calls += 1
        return None


def test_durable_webhook_encrypts_update_before_acknowledging():
    application = _application()
    application.process_update = AsyncMock()
    inbox = _EncryptedQueueInbox()
    client_app = create_webhook_app(application=application, inbox=inbox)

    with TestClient(client_app) as client:
        response = _post(client, json=_payload())

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    assert inbox.enqueued == {123: _payload()}
    assert inbox.claim_next_calls >= 1
    application.process_update.assert_not_called()
    application.update_queue.put.assert_not_awaited()


def test_durable_webhook_acknowledges_duplicate_after_durable_insert():
    application = _application()
    inbox = _EncryptedQueueInbox()
    client_app = create_webhook_app(application=application, inbox=inbox)

    with TestClient(client_app) as client:
        first = _post(client, json=_payload())
        duplicate = _post(client, json=_payload())

    assert first.status_code == 202
    assert duplicate.status_code == 202
    assert inbox.enqueued == {123: _payload()}
    application.process_update.assert_not_awaited()


def test_durable_webhook_returns_retryable_status_when_encrypted_insert_fails():
    application = _application()
    inbox = _EncryptedQueueInbox(fail=True)
    client_app = create_webhook_app(application=application, inbox=inbox)

    with TestClient(client_app) as client:
        response = _post(client, json=_payload())

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Telegram update could not be durably accepted; retry delivery"
    )
    assert "secret narrative" not in response.text
    application.process_update.assert_not_awaited()
