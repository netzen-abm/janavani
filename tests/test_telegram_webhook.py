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
    response = client.post(
        "/telegram/webhook",
        json=_payload(),
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )
    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    application.update_queue.put.assert_awaited_once()


def test_webhook_returns_retryable_status_if_queue_rejects_update():
    application = _application()
    application.update_queue.put.side_effect = RuntimeError("queue unavailable")
    client = TestClient(create_webhook_app(application=application))

    response = client.post(
        "/telegram/webhook",
        json=_payload(),
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Telegram update could not be queued; retry delivery"
    )


def test_webhook_liveness_is_available():
    client = TestClient(create_webhook_app(application=_application()))
    response = client.get("/liveness")
    assert response.status_code == 200
    assert response.json() == {
        "status": "alive",
        "surface": "telegram-webhook",
    }
