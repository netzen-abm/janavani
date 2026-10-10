
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.identity.pairing import IdentityPairingService, InMemoryPairingRepository
import src.web.identity_pairing_router as pairing_router


def authenticated_context():
    return IdentityContext(principal=Principal(principal_id="citizen:test", interface="webapp"))


def test_pairing_routes_fail_closed_when_shared_store_is_not_configured(monkeypatch):
    monkeypatch.setattr(pairing_router, "_pairing_service", None)
    app = FastAPI()
    app.include_router(pairing_router.router)
    app.dependency_overrides[pairing_router.require_authenticated_identity] = authenticated_context
    response = TestClient(app).post("/civic/identity-pairings")
    assert response.status_code == 503
    assert response.json()["detail"].startswith("Cross-surface pairing requires shared PostgreSQL")


def test_pairing_route_issues_no_store_challenge_and_requires_confirmation(monkeypatch):
    service = IdentityPairingService(InMemoryPairingRepository())
    monkeypatch.setattr(pairing_router, "_pairing_service", service)
    app = FastAPI()
    app.include_router(pairing_router.router)
    app.dependency_overrides[pairing_router.require_authenticated_identity] = authenticated_context
    client = TestClient(app)

    issued = client.post("/civic/identity-pairings")
    assert issued.status_code == 200
    assert issued.headers["cache-control"] == "no-store"
    challenge = issued.json()
    assert challenge["code"]
    assert challenge["expires_at"]

    service.claim_telegram(challenge["code"], telegram_subject="telegram:123")
    rejected = client.post(
        f"/civic/identity-pairings/{challenge['pairing_id']}/confirm",
        json={"explicit_confirmation": False},
    )
    assert rejected.status_code == 403

    confirmed = client.post(
        f"/civic/identity-pairings/{challenge['pairing_id']}/confirm",
        json={"explicit_confirmation": True},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["linked"] is True
    assert confirmed.json()["verified"] is True


def test_pairing_confirmation_cannot_be_replayed(monkeypatch):
    service = IdentityPairingService(InMemoryPairingRepository())
    challenge = service.issue(principal_id="citizen:test")
    service.claim_telegram(challenge.code, telegram_subject="telegram:123")
    service.confirm_from_web(
        challenge.pairing_id, principal_id="citizen:test", explicit_confirmation=True,
    )
    with pytest.raises(LookupError):
        service.confirm_from_web(
            challenge.pairing_id, principal_id="citizen:test", explicit_confirmation=True,
        )
