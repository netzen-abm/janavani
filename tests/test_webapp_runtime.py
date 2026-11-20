from fastapi.testclient import TestClient


def test_webapp_registers_case_workspace_routes():
    from src.webapp.main import app

    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/" in paths
    assert "/submit-issue" in paths
    assert "/local-vault/scope" in paths
    assert "/cases/{case_id}/prepare" in paths
    assert "/cases/{case_id}/review" in paths
    assert "/cases/{case_id}/consent" in paths
    assert "/cases/{case_id}/artifact" in paths


def test_case_creation_requires_explicit_consent_before_calling_api(monkeypatch):
    import src.webapp.main as webapp

    api_calls = []
    monkeypatch.setattr(
        webapp,
        "client_for_request",
        lambda request: api_calls.append(request),
    )
    response = TestClient(webapp.app).post(
        "/submit-issue",
        data={"citizen_input": "A private citizen issue narrative."},
    )

    assert response.status_code == 200
    assert "Local draft required" in response.text
    assert "No Case was created" in response.text
    assert api_calls == []


def test_webapp_case_creation_fails_closed_without_user_identity(monkeypatch):
    from src.webapp.main import app

    monkeypatch.delenv("JANAVANI_WEB_IDENTITY_ASSERTION", raising=False)
    response = TestClient(app).post(
        "/submit-issue",
        data={
            "local_draft_id": "local-12345678-abcd",
            "citizen_input": "The public streetlight has been out for three nights.",
        },
    )
    assert response.status_code == 200
    assert "Sign-in required" in response.text


def test_case_workspace_routes_execute_review_consent_and_ephemeral_download(monkeypatch):
    import src.webapp.case_workspace as workspace
    from src.webapp.main import app

    class Client:
        identity_assertion = "test-signed-assertion"

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

def test_case_workspace_requires_request_identity_before_protected_calls():
    from src.webapp.main import app

    response = TestClient(app).get("/cases/case-private/prepare")
    assert response.status_code == 200
    assert "Sign-in required" in response.text
    assert "secure Janavani session" in response.text

def test_webapp_owns_the_canonical_drafting_and_saved_format_ui():
    from src.webapp.main import app

    paths = {getattr(route, "path", "") for route in app.routes}

    assert "/ai-drafting" in paths
    assert "/ai-drafting/preview" in paths
    assert "/citizen-formats" in paths
    assert "/citizen-formats/confirm" in paths
    assert not any(path.startswith("/bill-review/") for path in paths)
    assert "/dispatch-objection" not in paths


def test_webapp_serves_the_first_party_local_vault_adapter():
    from src.webapp.main import app

    response = TestClient(app).get("/assets/janavani-local-vault")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/javascript")
    assert "indexedDB.open" in response.text
    assert "JanavaniLocalVault" in response.text
    assert "local-vault/scope" in response.text

    controller = TestClient(app).get("/assets/janavani-local-draft-form")
    assert controller.status_code == 200
    assert controller.headers["content-type"].startswith("application/javascript")
    assert "checkAccountScope" in controller.text


def test_submit_issue_creates_metadata_shell_without_forwarding_narrative(monkeypatch):
    import src.webapp.main as webapp

    calls = []

    class Client:
        def create_case_shell(self, *, case_type):
            calls.append({"case_type": case_type})
            return {"case_id": "case-shell-test", "status": "draft"}

    monkeypatch.setattr(webapp, "client_for_request", lambda request: Client())
    response = TestClient(webapp.app).post(
        "/submit-issue",
        data={
            "local_draft_id": "local-12345678-abcd",
            "case_type": "complaint",
            "citizen_input": "This private narrative must not be sent to the server.",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "case_id": "case-shell-test",
        "status": "draft",
        "content_transmitted": False,
    }
    assert calls == [{"case_type": "complaint"}]


def test_submit_issue_rejects_missing_local_draft_reference_before_api_call(monkeypatch):
    import src.webapp.main as webapp

    calls = []
    monkeypatch.setattr(
        webapp,
        "client_for_request",
        lambda request: calls.append(request),
    )
    response = TestClient(webapp.app).post(
        "/submit-issue",
        data={"case_type": "complaint", "citizen_input": "Private narrative"},
    )
    assert response.status_code == 200
    assert "Local draft required" in response.text
    assert calls == []


def test_local_vault_scope_route_proxies_authenticated_scope(monkeypatch):
    import src.webapp.main as webapp

    class Client:
        def get_local_vault_scope(self):
            return {"scope": "a" * 64}

    monkeypatch.setattr(webapp, "client_for_request", lambda request: Client())
    response = TestClient(webapp.app).get("/local-vault/scope")
    assert response.status_code == 200
    assert response.json() == {"scope": "a" * 64}



def test_home_page_renders_local_draft_workspace_and_storage_disclosure():
    from src.webapp.main import app

    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "local-case-draft-form" in response.text
    assert "janavani-local-draft-form.js" in response.text
    assert "not encrypted by Janavani" in response.text


def test_local_vault_scope_proxy_is_private_and_uncached(monkeypatch):
    import src.webapp.main as webapp

    class Client:
        def get_local_vault_scope(self):
            return {"scope": "b" * 64}

    monkeypatch.setattr(webapp, "client_for_request", lambda request: Client())
    response = TestClient(webapp.app).get("/local-vault/scope")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, private"
    assert response.headers["pragma"] == "no-cache"
