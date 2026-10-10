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


def test_case_workspace_routes_execute_review_consent_and_ephemeral_download(monkeypatch):
    import src.webapp.case_workspace as workspace
    from src.webapp.main import app

    class Client:
        def get_case(self, case_id):
            return {"case_id": case_id, "status": "draft"}

        def prepare_document_draft(self, case_id):
            return {
                "case_id": case_id,
                "document_id": "doc-test",
                "subject": "Streetlight outage",
                "body": "The streetlight has been out for three nights.",
            }

        def review_document(self, case_id, **kwargs):
            return {"document_id": kwargs["document_id"], "status": "reviewed"}

        def start_review(self, case_id, **kwargs):
            return {"status": "review"}

        def record_explicit_consent(self, case_id):
            return {"status": "ready"}

        def generate_artifact(self, case_id, **kwargs):
            assert kwargs["document_id"] == "doc-test"
            assert kwargs["document_format"] == "pdf"
            return b"%PDF-test-payload"

    monkeypatch.setattr(workspace, "client_for_request", lambda request: Client())
    client = TestClient(app)

    prepared = client.get("/cases/case-test/prepare")
    assert prepared.status_code == 200
    assert "Streetlight outage" in prepared.text

    reviewed = client.post(
        "/cases/case-test/review",
        data={
            "subject": "Streetlight outage",
            "body": "The streetlight has been out for three nights.",
            "reason": "Citizen correction",
        },
    )
    assert reviewed.status_code == 200
    assert "Draft saved for review" in reviewed.text

    consented = client.post(
        "/cases/case-test/consent",
        data={"explicit_confirmation": "yes"},
    )
    assert consented.status_code == 200
    assert "Explicit consent recorded" in consented.text

    artifact = client.post(
        "/cases/case-test/artifact", data={"document_format": "pdf"}
    )
    assert artifact.status_code == 200
    assert artifact.content == b"%PDF-test-payload"
    assert artifact.headers["cache-control"] == "no-store, private"

