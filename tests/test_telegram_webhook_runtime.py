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
