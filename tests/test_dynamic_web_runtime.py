from fastapi.testclient import TestClient

from src.dynamic_web.main import _PATHWAYS, app
from src.documents.template_catalogue import get_template


def test_dynamic_website_is_a_separate_product_runtime_with_preamble_first():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "WE, THE PEOPLE OF INDIA" in response.text
    assert "Find a civic pathway" in response.text
    assert "Draft a civic document" in response.text
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

