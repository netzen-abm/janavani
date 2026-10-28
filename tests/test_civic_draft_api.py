from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.web.civic_draft_router import router


def _app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_preview_is_rejected_without_explicit_server_processing_consent():
    response = TestClient(_app()).post(
        "/civic/drafts/preview",
        json={
            "template_id": "complaint.general",
            "issue": "Do not forward this without consent.",
        },
    )
    assert response.status_code == 403
    assert "consent" in response.json()["detail"].lower()


def test_unauthenticated_local_preview_is_allowed_but_not_persisted():
    response = TestClient(_app()).post(
        "/civic/drafts/preview",
        json={
            "template_id": "complaint.general",
            "issue": "The public streetlight has been out for three nights.",
            "preview_processing_consent": True,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "preview"
    assert body["ai_used"] is False
    assert body["persistence"] == "not_persisted"
    assert body["submission"] == "not_submitted"
    assert response.headers["cache-control"] == "no-store, private"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "The public streetlight has been out for three nights." in body["draft_body"]


def test_rti_api_requires_jurisdiction_and_existing_record_requests():
    response = TestClient(_app()).post(
        "/civic/drafts/preview",
        json={
            "template_id": "rti.records",
            "issue": "Please provide records about road repairs.",
            "preview_processing_consent": True,
        },
    )
    assert response.status_code == 422
    assert "jurisdiction" in response.json()["detail"].lower()


def test_remote_ai_without_identity_returns_local_preview_without_ai_call(monkeypatch):
    from src.core.settings import ai_settings

    monkeypatch.setattr(ai_settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(ai_settings, "LEGAL_DRAFTING_MODEL", "test-model")
    response = TestClient(_app()).post(
        "/civic/drafts/preview",
        json={
            "template_id": "complaint.general",
            "issue": "The road needs repair.",
            "preview_processing_consent": True,
            "use_ai": True,
            "remote_processing_consent": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ai_status"] == "identity_required"
    assert body["ai_used"] is False
    assert "The road needs repair." in body["draft_body"]


def test_invalid_authorization_fails_closed(monkeypatch):
    monkeypatch.setenv("JANAVANI_IDENTITY_ASSERTION_SECRET", "test-secret")
    response = TestClient(_app()).post(
        "/civic/drafts/preview",
        headers={"Authorization": "Bearer definitely-invalid"},
        json={
            "template_id": "complaint.general",
            "issue": "The drain is blocked.",
            "preview_processing_consent": True,
        },
    )
    assert response.status_code == 401
