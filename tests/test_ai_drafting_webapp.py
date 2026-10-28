from fastapi.testclient import TestClient


def test_ai_drafting_page_is_registered_and_explains_remote_processing():
    from src.webapp.main import app

    response = TestClient(app).get("/ai-drafting")
    assert response.status_code == 200
    assert "Draft a civic document" in response.text
    assert "RTI application — request for existing records" in response.text
    assert "Administrative notice reply — demand for documentary evidence" in response.text
    assert "configured remote AI provider" in response.text
    assert "Foundational questions or interrogatories" in response.text
    assert "Requested safeguards or administrative conditions" in response.text
    assert "Rights or remedies to reserve" in response.text
    assert "Requested response period" in response.text
    assert "Requested date" in response.text
    assert "Generate preview" in response.text


def test_webapp_sends_local_preview_without_identity(monkeypatch):
    import src.webapp.ai_drafting as drafting
    from src.webapp.main import app

    class Client:
        def __init__(self):
            self.payload = None

        def preview_civic_draft(self, payload):
            self.payload = payload
            return {
                "template_id": payload["template_id"],
                "template_version": 1,
                "ai_used": False,
                "ai_status": "not_requested",
                "message": "Preview generated locally.",
                "draft_body": "Civic complaint preview for review.",
                "persistence": "not_persisted",
                "submission": "not_submitted",
            }

    fake = Client()
    monkeypatch.setattr(drafting, "client_for_request", lambda request: fake)
    response = TestClient(app).post(
        "/ai-drafting/preview",
        data={
            "template_id": "complaint.general",
            "issue": "The drain is blocked.",
            "requested_documents": "",
        },
    )

    assert response.status_code == 200
    assert fake.payload["use_ai"] is False
    assert fake.payload["remote_processing_consent"] is False
    assert "Civic complaint preview for review." in response.text
    assert "AI used: No" in response.text
    assert "not saved" in response.text.lower()


def test_webapp_remote_ai_requires_explicit_checkbox_and_reports_status(monkeypatch):
    import src.webapp.ai_drafting as drafting
    from src.webapp.main import app

    class Client:
        def preview_civic_draft(self, payload):
            assert payload["use_ai"] is True
            assert payload["remote_processing_consent"] is True
            return {
                "template_id": "representation.general",
                "template_version": 1,
                "ai_used": False,
                "ai_status": "identity_required",
                "message": "A verified identity is required for remote AI drafting.",
                "draft_body": "Deterministic preview remains available.",
                "persistence": "not_persisted",
                "submission": "not_submitted",
            }

    monkeypatch.setattr(drafting, "client_for_request", lambda request: Client())
    response = TestClient(app).post(
        "/ai-drafting/preview",
        headers={"Origin": "http://testserver"},
        data={
            "template_id": "representation.general",
            "issue": "Please consider the attached citizen representation.",
            "use_ai": "yes",
            "remote_processing_consent": "yes",
        },
    )
    assert response.status_code == 200
    assert "identity_required" in response.text
    assert "Deterministic preview remains available." in response.text


def test_cross_origin_remote_ai_request_fails_closed_to_local_preview(monkeypatch):
    import src.webapp.ai_drafting as drafting
    from src.webapp.main import app

    class Client:
        def preview_civic_draft(self, payload):
            assert payload["use_ai"] is True
            assert payload["remote_processing_consent"] is False
            return {
                "template_id": "complaint.general",
                "template_version": 1,
                "ai_used": False,
                "ai_status": "consent_required",
                "message": "No remote AI call was made.",
                "draft_body": "Local-only preview.",
                "persistence": "not_persisted",
                "submission": "not_submitted",
            }

    monkeypatch.setattr(drafting, "client_for_request", lambda request: Client())
    response = TestClient(app).post(
        "/ai-drafting/preview",
        headers={"Origin": "https://attacker.example"},
        data={
            "template_id": "complaint.general",
            "issue": "An ordinary civic issue.",
            "use_ai": "yes",
            "remote_processing_consent": "yes",
        },
    )
    assert response.status_code == 200
    assert "consent_required" in response.text
    assert "Local-only preview." in response.text


def test_webapp_routes_administrative_evidence_demand_through_shared_preview(monkeypatch):
    import src.webapp.ai_drafting as drafting
    from src.webapp.main import app

    class Client:
        def preview_civic_draft(self, payload):
            assert payload["template_id"] == "administrative.evidence-demand"
            assert payload["jurisdiction"] == "Kerala municipal authority"
            assert payload["use_ai"] is False
            return {
                "template_id": payload["template_id"],
                "template_version": 1,
                "ai_used": False,
                "ai_status": "not_requested",
                "message": "Saved structural defaults applied.",
                "draft_body": "Part I — Foundational and constitutional questions\nPart II — Documents and records requested",
                "persistence": "not_persisted",
                "submission": "not_submitted",
            }

    monkeypatch.setattr(drafting, "client_for_request", lambda request: Client())
    response = TestClient(app).post(
        "/ai-drafting/preview",
        data={
            "template_id": "administrative.evidence-demand",
            "issue": "The municipality has demanded a recurring sanitation levy.",
            "jurisdiction": "Kerala municipal authority",
        },
    )

    assert response.status_code == 200
    assert "Administrative notice reply — demand for documentary evidence" in response.text
    assert "Foundational and constitutional questions" in response.text
    assert "Documents and records requested" in response.text

def test_webapp_can_preselect_a_template_from_the_pathway_selector():
    import re
    from src.webapp.main import app

    response = TestClient(app).get("/ai-drafting?template_id=rti.records")
    assert response.status_code == 200
    selected_options = re.findall(r"<option\b[^>]*selected[^>]*>", response.text)
    assert any('value="rti.records"' in option for option in selected_options)
