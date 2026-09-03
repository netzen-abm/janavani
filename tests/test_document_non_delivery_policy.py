"""Guardrails for JanaVani's user-controlled document delivery boundary."""
from documents.document_contract import DocumentDraft, DocumentParty


def test_document_draft_contains_destination_for_user_review_only():
    draft = DocumentDraft(
        document_id="DOC-1",
        document_type="complaint",
        case_id="CASE-1",
        date="03-09-2026",
        subject="Test complaint",
        body="Test body",
        to=DocumentParty(
            name="Test Office",
            address="Test Address",
            email="office@example.gov.in",
        ),
    )

    text = draft.as_text()

    assert "To:" in text
    assert "office@example.gov.in" in text
    assert "send" not in text.lower()


def test_document_contract_has_no_delivery_transport():
    fields = set(DocumentDraft.__dataclass_fields__)

    assert "smtp" not in fields
    assert "delivery_url" not in fields
    assert "submission_endpoint" not in fields
