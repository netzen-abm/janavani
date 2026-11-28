from fastapi.testclient import TestClient


def test_webapp_serves_the_shared_packaged_brand_mark():
    from src.webapp.main import app

    response = TestClient(app).get("/brand-assets/brand/janavani-mark")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert response.headers["cache-control"] == "public, max-age=86400"
    assert '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="702" height="694">' in response.text



def test_webapp_home_keeps_styles_in_head_and_uses_the_selected_brand():
    from src.webapp.main import app

    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.text.count("<h1") == 1
    assert response.text.index("body { padding: 2rem 0;") < response.text.index("</head>")
    assert 'src="/brand-assets/brand/janavani-mark"' in response.text
    assert 'href="/favicon.svg"' in response.text
    assert 'class="container"' in response.text

    favicon = TestClient(app).get("/favicon.svg")
    assert favicon.status_code == 200
    assert favicon.headers["content-type"].startswith("image/svg+xml")
    assert len(favicon.content) > 100_000


def test_webapp_serves_imported_webp_illustrations():
    from src.webapp.main import app

    for path in (
        "/brand-assets/illustrations/preamble-of-india",
        "/brand-assets/illustrations/civic-action-pathway",
    ):
        response = TestClient(app).get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/webp")
        assert response.headers["cache-control"] == "public, max-age=86400"
        assert len(response.content) > 1000


def test_ai_drafting_page_is_registered_and_explains_remote_processing():
    from src.webapp.main import app

    response = TestClient(app).get("/ai-drafting")
    assert response.status_code == 200
    assert "Draft a civic document" in response.text
    assert "RTI application — request for existing records" in response.text
    assert "Administrative notice reply — demand for documentary evidence" in response.text
    assert "Remote AI improvement is temporarily disabled" in response.text
    assert "server-side deterministic processing, not browser-local processing" in response.text
    assert "Foundational questions or interrogatories" in response.text
    assert "Requested safeguards or administrative conditions" in response.text
    assert "Rights or remedies to reserve" in response.text
    assert "Requested response period" in response.text
    assert "Requested date" in response.text
    assert "Generate preview" in response.text


def test_webapp_sends_consented_deterministic_preview_without_identity(monkeypatch):
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
                "message": "Deterministic server-side preview generated after explicit consent.",
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
            "preview_processing_consent": "yes",
        },
    )

    assert response.status_code == 200
    assert fake.payload["use_ai"] is False
    assert fake.payload["remote_processing_consent"] is False
    assert "Civic complaint preview for review." in response.text
    assert "Deterministic server-side preview generated after explicit consent." in response.text
    assert "AI used: No" in response.text
    assert "not saved" in response.text.lower()


def test_webapp_cannot_enable_remote_ai_from_raw_text_form_fields(monkeypatch):
    import src.webapp.ai_drafting as drafting
    from src.webapp.main import app

    class Client:
        def preview_civic_draft(self, payload):
            assert payload["preview_processing_consent"] is True
            # Remote-AI fields are intentionally not accepted by the shared form.
            assert payload["use_ai"] is False
            assert payload["remote_processing_consent"] is False
            return {
                "template_id": "representation.general",
                "template_version": 1,
                "ai_used": False,
                "ai_status": "not_requested",
                "message": "Deterministic preview remains available; remote AI is disabled pending privacy-safe input minimization.",
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
            "preview_processing_consent": "yes",
            # Even forged legacy form fields cannot re-enable remote AI.
            "use_ai": "yes",
            "remote_processing_consent": "yes",
        },
    )
    assert response.status_code == 200
    assert "AI used: No" in response.text
    assert "remote AI is disabled pending privacy-safe input minimization" in response.text


def test_origin_or_forged_fields_cannot_reenable_remote_ai(monkeypatch):
    import src.webapp.ai_drafting as drafting
    from src.webapp.main import app

    class Client:
        def preview_civic_draft(self, payload):
            assert payload["use_ai"] is False
            assert payload["remote_processing_consent"] is False
            return {
                "template_id": "complaint.general",
                "template_version": 1,
                "ai_used": False,
                "ai_status": "not_requested",
                "message": "Remote AI is disabled pending privacy-safe input minimization.",
                "draft_body": "Deterministic server-side preview.",
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
            "preview_processing_consent": "yes",
            "use_ai": "yes",
            "remote_processing_consent": "yes",
        },
    )
    assert response.status_code == 200
    assert "AI used: No" in response.text
    assert "Remote AI is disabled pending privacy-safe input minimization." in response.text


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
            "preview_processing_consent": "yes",
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
