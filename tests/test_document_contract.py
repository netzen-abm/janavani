from datetime import date

import pytest

from documents.complaint_builder import build_complaint
from documents.document_contract import DocumentRequest, StructuredDocument
from documents.document_engine import DocumentEngine


def test_document_request_normalizes_type():
    request = DocumentRequest(
        document_type=" Complaint ",
        user_name="Citizen",
        user_address="Address",
        office_id="OFF-1",
        issue_text="Service delayed",
    )
    assert request.document_type == "complaint"


def test_document_request_rejects_unknown_type():
    with pytest.raises(ValueError):
        DocumentRequest(
            document_type="unknown",
            user_name="Citizen",
            user_address="Address",
            office_id="OFF-1",
            issue_text="Issue",
        )


def test_document_request_rejects_empty_issue():
    with pytest.raises(ValueError):
        DocumentRequest(
            document_type="complaint",
            user_name="Citizen",
            user_address="Address",
            office_id="OFF-1",
            issue_text="   ",
        )


def test_complaint_builder_returns_structured_document():
    document = build_complaint(
        "Citizen", "Address", "OFF-1", "ration denied"
    )
    assert isinstance(document, StructuredDocument)
    assert document.document_type == "complaint"
    assert document.created_on == date.today()
    assert document.content["office_id"] == "OFF-1"
    assert document.content["issue"] == "ration denied"
    assert document.document_id.startswith("JV-")


def test_document_engine_uses_canonical_builder():
    request = DocumentRequest(
        document_type="complaint",
        user_name="Citizen",
        user_address="Address",
        office_id="OFF-1",
        issue_text="ration denied",
    )
    document = DocumentEngine().generate(request)
    assert isinstance(document, StructuredDocument)
    assert document.document_type == "complaint"
