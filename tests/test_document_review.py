from src.core.capabilities.document_preparation import DocumentDraft
from src.core.capabilities.document_review import CorrectionVerification, SharedDocumentReview


def draft():
    return DocumentDraft(
        document_id="doc-1",
        document_type="complaint",
        to_name="Authority",
        to_address="Old Address",
        to_email="old@example.gov",
        cc_name=None,
        cc_address=None,
        cc_email=None,
        subject="Broken road",
        body="Please inspect the road.",
        source_case_id="case-1",
    )


def test_citizen_can_correct_content_and_address():
    service = SharedDocumentReview()
    c1 = service.propose_correction(draft(), field="to_address", new_value="Correct Address")
    c2 = service.propose_correction(draft(), field="body", new_value="Updated complaint")
    assert c1.verification == CorrectionVerification.PENDING
    revised = service.apply_local_revision(draft(), (c1, c2))
    assert revised.to_address == "Correct Address"
    assert revised.body == "Updated complaint"
    assert revised.submission_enabled is False


def test_non_document_field_cannot_be_edited():
    service = SharedDocumentReview()
    try:
        service.propose_correction(draft(), field="source_case_id", new_value="case-2")
    except ValueError as exc:
        assert "not editable" in str(exc)
    else:
        raise AssertionError("case linkage must not be editable")
