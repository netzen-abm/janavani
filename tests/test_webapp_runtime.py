from fastapi.testclient import TestClient


def test_webapp_registers_case_workspace_routes():
    from src.webapp.main import app

    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/" in paths
    assert "/submit-issue" in paths
    assert "/cases/{case_id}/prepare" in paths
    assert "/cases/{case_id}/review" in paths
    assert "/cases/{case_id}/consent" in paths
    assert "/cases/{case_id}/artifact" in paths


def test_webapp_case_creation_fails_closed_without_user_identity(monkeypatch):
    from src.webapp.main import app

    monkeypatch.delenv("JANAVANI_WEB_IDENTITY_ASSERTION", raising=False)
    response = TestClient(app).post(
        "/submit-issue",
        data={"citizen_input": "The public streetlight has been out for three nights."},
    )
    assert response.status_code == 200
    assert "Sign-in required" in response.text
