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


def test_case_lifecycle_routes_explicitly_disable_submission():
    from pathlib import Path

    source = Path("src/web/civic_case_lifecycle_router.py").read_text(encoding="utf-8")

    assert "Janavani never submits documents or petitions" in source
    assert "Janavani never queues or transmits document submissions" in source


def test_ephemeral_artifact_payload_is_not_persisted():
    from src.documents.artifact_service import render_artifact_payload

    draft = DocumentDraft(
        document_id="DOC-EPHEMERAL",
        document_type="complaint",
        case_id="CASE-EPHEMERAL",
        date="2026-10-07",
        subject="Ephemeral test",
        body="Do not persist this payload.",
        to=DocumentParty(name="Test Office"),
    )
    payload = render_artifact_payload(draft, __import__("src.documents.document_contract", fromlist=["DocumentFormat"]).DocumentFormat.PDF)
    assert payload.content
    assert payload.content_sha256
    assert "storage_ref" not in payload.__dataclass_fields__
