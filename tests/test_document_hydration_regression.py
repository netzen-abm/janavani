import pytest

from src.domain.document import DocumentType
from src.storage.hydration import document_from_row


def test_document_hydration_uses_to_party_and_required_text_fields() -> None:
    row = {
        "document_id": "DOC-1",
        "document_type": DocumentType.COMPLAINT.value,
        "title": "Complaint",
        "language": "en",
        "to_party": {"party_type": "office", "name": "Example Office"},
        "subject": "Delayed service",
        "body": "Please investigate.",
        "status": "draft",
        "version": 1,
    }
    document = document_from_row(row)
    assert document.to_party.name == "Example Office"
    assert document.subject == "Delayed service"
    assert document.body == "Please investigate."


def test_document_hydration_rejects_missing_recipient() -> None:
    row = {
        "document_id": "DOC-1",
        "document_type": DocumentType.COMPLAINT.value,
        "title": "Complaint",
        "language": "en",
        "subject": "Delayed service",
        "body": "Please investigate.",
    }
    with pytest.raises(ValueError, match="to_party"):
        document_from_row(row)
