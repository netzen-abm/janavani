from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from src.web import telegram_webhook_app


class FakeInbox:
    def __init__(self, *, fail=False):
        self.accepted = []
        self.ids = set()
        self.fail = fail

    def accept(self, update_id, payload):
        if self.fail:
            raise OSError("database unavailable")
        if update_id in self.ids:
            return False
        self.ids.add(update_id)
        self.accepted.append((update_id, payload))
        return True


def _payload():
    return {"update_id": 9001, "message": {"message_id": 7, "date": 1,
            "chat": {"id": 5, "type": "private"},
            "from": {"id": 5, "is_bot": False, "first_name": "Citizen"},
            "text": "/start"}}


def _client(monkeypatch, inbox):
    bot_app = MagicMock()
    monkeypatch.setattr(telegram_webhook_app.Update, "de_json",
                        lambda payload, bot: MagicMock(update_id=payload["update_id"]))
    app = telegram_webhook_app.create_webhook_app(application=bot_app, inbox=inbox)
    return TestClient(app)


def test_webhook_persists_update_before_acknowledging(monkeypatch):
    inbox = FakeInbox()
    response = _client(monkeypatch, inbox).post(
        "/telegram/webhook", json=_payload(),
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )
    assert response.status_code == 202
    assert inbox.accepted[0][0] == 9001
    client = _client(monkeypatch, inbox)
    client.app.state.telegram_application.update_queue.put.assert_not_called()
    # Durable inbox owns acceptance; the process-local PTB queue is not used.


def test_webhook_returns_retryable_failure_if_durable_acceptance_fails(monkeypatch):
    inbox = FakeInbox(fail=True)
    response = _client(monkeypatch, inbox).post(
        "/telegram/webhook", json=_payload(),
        headers={"X-Telegram-Bot-Api-Secret-Token": "test-secret"},
    )
    assert response.status_code == 503


def test_duplicate_webhook_update_is_acknowledged_without_duplicate_acceptance(monkeypatch):
    inbox = FakeInbox()
    client = _client(monkeypatch, inbox)
    headers = {"X-Telegram-Bot-Api-Secret-Token": "test-secret"}
    assert client.post("/telegram/webhook", json=_payload(), headers=headers).status_code == 202
    assert client.post("/telegram/webhook", json=_payload(), headers=headers).status_code == 202
    assert len(inbox.accepted) == 1
