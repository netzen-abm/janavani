from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

import src.webapp.identity_pairing_workspace as pairing_workspace


class _PairingClient:
    def __init__(self, *, base_url, identity_assertion):
        self.base_url = base_url
        self.identity_assertion = identity_assertion
        self.issue_calls = 0
        self.confirm_calls = []

    def issue(self):
        self.issue_calls += 1
        return {
            "pairing_id": "pairing-123",
            "code": "safe-test-code",
            "expires_at": "2026-10-22T12:05:00+00:00",
        }

    def confirm(self, pairing_id):
        self.confirm_calls.append(pairing_id)
        if getattr(self, "confirm_error", None):
            raise self.confirm_error
        return {
            "linked": True,
            "provider": "telegram",
            "authentication_method": "web_telegram_pairing",
            "verified": True,
        }


def _setup(monkeypatch):
    from src.webapp.main import app

    monkeypatch.setattr(
        pairing_workspace,
        "client_for_request",
        lambda request: SimpleNamespace(
            base_url="https://api.janavani.test",
            identity_assertion="verified-request-assertion",
        ),
    )
    monkeypatch.setattr(pairing_workspace, "IdentityPairingAPIClient", _PairingClient)
    client = TestClient(app, base_url="https://janavani.test")
    client.cookies.set("janavani_identity_assertion", "opaque-test-cookie")
    return client


def _origin():
    return {"Origin": "https://janavani.test"}


def test_pairing_page_requires_explicit_start_and_is_not_cached(monkeypatch):
    client = _setup(monkeypatch)
    response = client.get("/identity/telegram/pair")
    assert response.status_code == 200
    assert "Generate pairing code" in response.text
    assert "does not link accounts" in response.text
    assert response.headers["cache-control"] == "no-store, private"


def test_pairing_start_shows_short_lived_code_and_explicit_confirmation(monkeypatch):
    client = _setup(monkeypatch)
    response = client.post("/identity/telegram/pair", headers=_origin())
    assert response.status_code == 200
    assert "safe-test-code" in response.text
    assert "/pair safe-test-code" in response.text
    assert "not linked until this confirmation succeeds" in response.text
    assert "/identity/telegram/pair/pairing-123/confirm" in response.text
    assert response.headers["cache-control"] == "no-store, private"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_pairing_confirmation_requires_checkbox_and_does_not_call_api(monkeypatch):
    client = _setup(monkeypatch)
    response = client.post(
        "/identity/telegram/pair/pairing-123/confirm",
        headers=_origin(),
    )
    assert response.status_code == 400
    assert "check the confirmation box" in response.text.lower()


def test_pairing_success_is_reported_only_after_verified_api_confirmation(monkeypatch):
    client = _setup(monkeypatch)
    response = client.post(
        "/identity/telegram/pair/pairing-123/confirm",
        data={"explicit_confirmation": "yes"},
        headers=_origin(),
    )
    assert response.status_code == 200
    assert "Success: your verified Telegram identity is linked" in response.text


def test_pairing_not_ready_does_not_claim_link_success(monkeypatch):
    client = _setup(monkeypatch)
    response = httpx.Response(
        409, request=httpx.Request("POST", "https://api.janavani.test/civic/identity-pairings/pairing-123/confirm")
    )
    pairing_workspace.IdentityPairingAPIClient.confirm_error = httpx.HTTPStatusError(
        "not claimed yet", request=response.request, response=response
    )
    try:
        result = client.post(
            "/identity/telegram/pair/pairing-123/confirm",
            data={"explicit_confirmation": "yes"},
            headers=_origin(),
        )
        assert result.status_code == 409
        assert "Pairing not ready" in result.text
        assert "Do not assume" not in result.text
    finally:
        del pairing_workspace.IdentityPairingAPIClient.confirm_error


def test_cookie_authenticated_pairing_post_rejects_cross_origin(monkeypatch):
    client = _setup(monkeypatch)
    response = client.post(
        "/identity/telegram/pair",
        headers={"Origin": "https://attacker.test"},
    )
    assert response.status_code == 403
    assert "Cross-origin browser mutation rejected" in response.text
