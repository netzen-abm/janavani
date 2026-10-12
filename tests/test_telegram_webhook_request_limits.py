from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from src.web.telegram_webhook_app import MAX_WEBHOOK_BODY_BYTES, create_webhook_app


def test_telegram_webhook_rejects_declared_oversized_body_before_parsing():
    application = MagicMock()
    client = TestClient(create_webhook_app(application=application))

    response = client.post(
        "/telegram/webhook",
        content=b"x" * (MAX_WEBHOOK_BODY_BYTES + 1),
        headers={
            "Content-Type": "application/json",
            "X-Telegram-Bot-Api-Secret-Token": "test-secret",
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Telegram update exceeds size limit"
    application.update_queue.put.assert_not_called()
