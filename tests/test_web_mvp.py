"""Regression tests for interactive Web MVP document templates."""
from io import BytesIO

import pytest
from docx import Document
from starlette.testclient import TestClient

from src.web_mvp.main import app, build_objection_document


def test_build_objection_document_pdf_is_a_pdf():
    """The PDF option returns bytes with a PDF media type and safe filename."""
    payload, media_type, filename = build_objection_document(
        "BILL-2026-KL-04", "Please publish the official bill text.", "pdf"
    )
    assert payload.startswith(b"%PDF-")
    assert media_type == "application/pdf"
    assert filename == "citizen_review_draft_BILL-2026-KL-04.pdf"


def test_build_objection_document_docx_preserves_user_observations():
    """The DOCX option keeps citizen-provided comments in an editable document."""
    payload, media_type, filename = build_objection_document(
        "BILL-2026-KL-04", "Please provide the source record.", "DOCX"
    )
    document = Document(BytesIO(payload))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Please provide the source record." in text
    assert "not legal advice" in text
    assert media_type.startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert filename.endswith(".docx")


def test_build_objection_document_rejects_unsafe_reference_and_format():
    """File references and formats are validated before filename construction."""
    with pytest.raises(ValueError):
        build_objection_document("../private/file", "comment", "PDF")
    with pytest.raises(ValueError):
        build_objection_document("BILL-1", "comment", "HTML")



def test_webapp_health_endpoint_returns_json():
    """Deployment health checks receive a simple non-sensitive response."""
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_home_page_exposes_interactive_draft_form():
    """The deployed WebApp home page renders the civic drafting entry point."""
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Prepare a civic grievance draft" in response.text
    assert 'action="/submit-issue"' in response.text


def test_submit_issue_delegates_and_marks_result_as_draft_only(monkeypatch):
    """A successful remote result remains clearly labelled as an unsubmitted draft."""
    class FakeWebClient:
        def request_document_draft(self, citizen_text):
            assert citizen_text == "broken road"
            return {
                "status": "available",
                "result": {
                    "choices": [
                        {"message": {"content": "Request that the road be repaired."}}
                    ]
                },
            }

    monkeypatch.setattr("src.web_mvp.main.JanavaniAIWebClient", FakeWebClient)
    response = TestClient(app).post(
        "/submit-issue", data={"citizen_input": "  broken road  "}
    )
    assert response.status_code == 200
    assert "Request that the road be repaired." in response.text
    assert "DRAFT ONLY" in response.text
    assert "does not register, file, or submit a complaint" in response.text


def test_submit_issue_rejects_oversized_input_before_calling_service(monkeypatch):
    """Very large public form submissions are stopped before upstream processing."""
    class MustNotBeCalled:
        def request_document_draft(self, citizen_text):
            raise AssertionError("oversized input must not reach the drafting service")

    monkeypatch.setattr("src.web_mvp.main.JanavaniAIWebClient", MustNotBeCalled)
    response = TestClient(app).post(
        "/submit-issue", data={"citizen_input": "x" * 4001}
    )
    assert response.status_code == 200
    assert "Please shorten your description" in response.text
    assert "has not been sent to the drafting service" in response.text


def test_submit_issue_rejects_blank_input_before_calling_service(monkeypatch):
    """Whitespace-only submissions do not consume a drafting-service request."""
    class MustNotBeCalled:
        def request_document_draft(self, citizen_text):
            raise AssertionError("blank input must not reach the drafting service")

    monkeypatch.setattr("src.web_mvp.main.JanavaniAIWebClient", MustNotBeCalled)
    response = TestClient(app).post(
        "/submit-issue", data={"citizen_input": "   "}
    )
    assert response.status_code == 200
    assert "Please describe the civic issue" in response.text
