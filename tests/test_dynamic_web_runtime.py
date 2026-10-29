from fastapi.testclient import TestClient

from src.dynamic_web.main import app
from src.dynamic_web.pathways import PATHWAYS as _PATHWAYS
from src.documents.template_catalogue import get_template


def test_dynamic_website_is_a_separate_product_runtime_with_preamble_first():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "WE, THE PEOPLE OF INDIA" in response.text
    assert "Find a civic pathway" in response.text
    assert "Draft a civic document" in response.text
    assert "/assets/illustrations/preamble-of-india.webp" in response.text
    assert "/assets/illustrations/civic-action-pathway.webp" in response.text
    assert "janavani-website" not in response.text


def test_dynamic_site_pathway_registry_resolves_only_canonical_templates():
    for pathway in _PATHWAYS.values():
        template = get_template(pathway["template_id"])
        assert template.template_id == pathway["template_id"]


def test_existing_records_pathway_recommends_rti_without_conflating_explanations():
    response = TestClient(app).post("/pathway", data={"purpose": "existing_records"})
    assert response.status_code == 200
    assert "RTI application" in response.text
    assert "existing records" in response.text.lower()
    assert "newly written explanation" in response.text
    assert "/ai-drafting?template_id=rti.records" in response.text


def test_fee_notice_pathway_reuses_administrative_evidence_demand_template():
    response = TestClient(app).post("/pathway", data={"purpose": "challenge_notice"})
    assert response.status_code == 200
    assert "Administrative notice reply" in response.text
    assert "does not establish that the fee is invalid" in response.text
    assert "/ai-drafting?template_id=administrative.evidence-demand" in response.text


def test_unknown_pathway_fails_closed_to_supported_selector():
    response = TestClient(app).post("/pathway", data={"purpose": "invented-pathway"})
    assert response.status_code == 200
    assert "Select one of the listed tasks" in response.text
    assert "Continue to this document format" not in response.text


def test_dynamic_site_registers_shared_template_first_drafting_flow():
    response = TestClient(app).get("/ai-drafting?template_id=rti.records")
    assert response.status_code == 200
    assert "Draft a civic document" in response.text
    assert "RTI application — request for existing records" in response.text
    assert "not saved or submitted" in response.text


def test_dynamic_site_forwards_administrative_fields_to_the_canonical_preview(monkeypatch):
    from src.adapters.janavani_platform_client import JanavaniWebAPIClient

    received = {}

    def fake_preview(self, payload):
        received.update(payload)
        return {
            "status": "preview",
            "template_id": payload["template_id"],
            "template_version": 1,
            "ai_used": False,
            "ai_status": "not_requested",
            "message": "Deterministic preview generated for review.",
            "draft_body": "Review this editable administrative draft.",
            "persistence": "not_persisted",
            "submission": "not_submitted",
        }

    monkeypatch.setattr(JanavaniWebAPIClient, "preview_civic_draft", fake_preview)
    response = TestClient(app).post(
        "/ai-drafting/preview",
        data={
            "template_id": "administrative.evidence-demand",
            "issue": "The local authority has imposed a recurring fee.",
            "preview_processing_consent": "yes",
            "jurisdiction": "Relevant municipal authority",
            "requested_documents": "Copy of the enabling order\nCopy of the calculation record",
            "part_i_interrogatories": "Identify the enabling law\nExplain the calculation method",
            "requested_conditions": "Provide a point-by-point response",
            "remedies_reserved": "Any lawful remedy available on the facts",
            "response_period": "14 days requested; verify applicable law",
            "deadline_date": "15 November 2026",
        },
    )

    assert response.status_code == 200, response.text
    assert received["requested_documents"] == [
        "Copy of the enabling order",
        "Copy of the calculation record",
    ]
    assert received["part_i_interrogatories"] == [
        "Identify the enabling law",
        "Explain the calculation method",
    ]
    assert received["requested_conditions"] == ["Provide a point-by-point response"]
    assert received["remedies_reserved"] == ["Any lawful remedy available on the facts"]
    assert received["response_period"] == "14 days requested; verify applicable law"
    assert received["deadline_date"] == "15 November 2026"
    assert received["preview_processing_consent"] is True
    assert received["use_ai"] is False
    assert received["remote_processing_consent"] is False


def test_dynamic_site_does_not_call_preview_api_without_processing_consent(monkeypatch):
    from src.adapters.janavani_platform_client import JanavaniWebAPIClient

    def forbidden_preview(self, payload):
        raise AssertionError("Preview API must not be called without consent")

    monkeypatch.setattr(JanavaniWebAPIClient, "preview_civic_draft", forbidden_preview)
    response = TestClient(app).post(
        "/ai-drafting/preview",
        data={
            "template_id": "complaint.general",
            "issue": "Sensitive test narrative that must not be forwarded.",
        },
    )

    assert response.status_code == 200
    assert "Processing consent required" in response.text
    assert "No request was forwarded to the canonical preview API" in response.text


def test_dynamic_site_serves_packaged_brand_mark_with_cache_headers():
    response = TestClient(app).get("/assets/brand/janavani-mark.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert response.headers["cache-control"] == "public, max-age=86400"
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in response.text
    assert "JanaVani" in response.text


def test_dynamic_site_serves_imported_webp_illustrations_with_cache_headers():
    for path in (
        "/assets/illustrations/preamble-of-india.webp",
        "/assets/illustrations/civic-action-pathway.webp",
    ):
        response = TestClient(app).get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/webp")
        assert response.headers["cache-control"] == "public, max-age=86400"
        assert len(response.content) > 1000


def test_dynamic_site_liveness_is_independent_of_api_and_telegram():
    response = TestClient(app).get("/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive", "surface": "dynamic-web"}


def test_dynamic_site_marks_post_responses_no_store():
    response = TestClient(app).post("/pathway", data={"purpose": "report_issue"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, private"
    assert response.headers["pragma"] == "no-cache"


def test_render_declares_dynamic_website_as_a_distinct_runtime():
    from pathlib import Path

    manifest = (Path(__file__).resolve().parents[1] / "render.yaml").read_text(encoding="utf-8")
    assert "name: janavani-dynamic-web" in manifest
    assert "uvicorn src.dynamic_web.main:app" in manifest
    assert "healthCheckPath: /liveness" in manifest

