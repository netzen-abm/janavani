from starlette.testclient import TestClient

from src.webapp.main import app


def test_homepage_offers_no_login_drafting_as_primary_path():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert 'name="narrative"' in response.text
    assert "/draft" in response.text
    assert "No account is needed" in response.text
    assert "Optional sign-in for tracking" in response.text


def test_anonymous_intake_recommends_and_previews_complaint_and_rti():
    narrative = (
        "The road is broken and unsafe. Please repair it and provide copies "
        "of the tender, work order and action-taken records."
    )
    response = TestClient(app).post("/draft", data={"narrative": narrative, "selection": "auto"})
    assert response.status_code == 200
    assert "complaint" in response.text.lower()
    assert "RTI" in response.text
    assert "Generate both" in response.text
    assert "does not create a tracked Case" in response.text
    assert response.headers["cache-control"] == "no-store, private"


def test_anonymous_intake_allows_rti_only_when_user_overrides_recommendation():
    response = TestClient(app).post(
        "/draft",
        data={"narrative": "The streetlight has been broken for a week.", "selection": "rti"},
    )
    assert response.status_code == 200
    assert "Draft application seeking information" in response.text
    assert "Draft civic complaint" not in response.text


def test_anonymous_pdf_and_docx_downloads_need_no_login_and_are_not_cached():
    client = TestClient(app)
    data = {
        "narrative": "The streetlight is broken and needs repair.",
        "document_type": "complaint",
    }
    pdf = client.post("/draft/download", data={**data, "document_format": "pdf"})
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF-")
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.headers["cache-control"] == "no-store, private"
    assert "attachment;" in pdf.headers["content-disposition"]

    docx = client.post("/draft/download", data={**data, "document_format": "docx"})
    assert docx.status_code == 200
    assert docx.content.startswith(b"PK")
    assert "wordprocessingml" in docx.headers["content-type"]


def test_invalid_anonymous_intake_fails_without_creating_a_case():
    response = TestClient(app).post("/draft", data={"narrative": "hi", "selection": "auto"})
    assert response.status_code == 422
    assert "No Case was created" in response.text
    assert response.headers["cache-control"] == "no-store, private"


def test_user_narrative_is_html_escaped_in_preview_and_download_controls():
    narrative = "The road is broken. <script>alert('x')</script>"
    response = TestClient(app).post("/draft", data={"narrative": narrative, "selection": "complaint"})
    assert response.status_code == 200
    assert "<script>" not in response.text
    assert "&lt;script&gt;" in response.text
