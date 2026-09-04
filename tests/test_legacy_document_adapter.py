from src.documents.document_contract import DocumentFormat
from src.documents.legacy_complaint_adapter import complaint_to_document_draft
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository
from src.documents.artifact_service import generate_artifact


def test_legacy_complaint_becomes_canonical_draft(tmp_path):
    repo = CsvAuthorityRepository("database/offices.csv")
    complaint = {
        "office_id": "1",
        "date": "03-09-2026",
        "issue": "Water supply complaint",
        "user": {"name": "Citizen", "address": "Edathala"},
        "law": {"law": "Test Act", "section": "1", "explanation": "Ground"},
    }
    draft = complaint_to_document_draft(
        complaint,
        document_id="JV1",
        case_id="JV1",
        authority_repository=repo,
    )
    assert draft.document_id == "JV1"
    assert draft.to.name == "Secretary"
    assert draft.sender is not None
    assert draft.legal_ground == "Test Act - 1 - Ground"


def test_artifact_has_content_hash(tmp_path):
    repo = InMemoryAuthorityRepository()
    # Keep this test independent of the CSV provider.
    from src.core.authority import AuthorityContact, AuthorityRecord

    repo.save(AuthorityRecord(
        authority_id="a1",
        name="Test Office",
        authority_type="Panchayat",
        primary_contact=AuthorityContact(
            name="Secretary", address="Test address", email="office@example.org"
        ),
    ))
    complaint = {
        "office_id": "a1",
        "date": "03-09-2026",
        "issue": "Test issue",
        "user": {"name": "Citizen", "address": "Test address"},
    }
    draft = complaint_to_document_draft(
        complaint,
        document_id="JV2",
        case_id="JV2",
        authority_repository=repo,
    )
    artifact = generate_artifact(draft, DocumentFormat.DOCX, tmp_path)
    assert artifact.reference.content_sha256
    assert artifact.reference.artifact_id == "JV2:docx"
    assert artifact.reference.state.value == "generated"
