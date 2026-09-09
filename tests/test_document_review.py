from src.core.document_review import DocumentReviewContract
from src.documents.document_contract import DocumentDraft, DocumentParty


def make_draft() -> DocumentDraft:
    return DocumentDraft(
        document_id="doc-1",
        document_type="representation",
        case_id="case-1",
        date="2026-09-09",
        subject="Original subject",
        body="Original body",
        to=DocumentParty(name="District Officer", address="Office"),
    )


def test_owner_can_edit_without_changing_document_identity():
    review = DocumentReviewContract(make_draft(), owner_id="citizen-1")

    edited = review.edit(
        actor_id="citizen-1",
        subject="Corrected subject",
        body="Corrected body",
        reason="Citizen correction",
    )

    assert edited.document_id == "doc-1"
    assert edited.case_id == "case-1"
    assert edited.subject == "Corrected subject"
    assert edited.body == "Corrected body"
    assert len(review.revisions) == 1
    assert review.revisions[0].actor_id == "citizen-1"


def test_non_owner_cannot_edit():
    review = DocumentReviewContract(make_draft(), owner_id="citizen-1")

    try:
        review.edit(actor_id="citizen-2", body="Tampered")
    except PermissionError:
        pass
    else:
        raise AssertionError("non-owner edit must fail")


def test_partial_edit_preserves_other_content():
    review = DocumentReviewContract(make_draft(), owner_id="citizen-1")

    edited = review.edit(actor_id="citizen-1", body="Only the body changed")

    assert edited.subject == "Original subject"
    assert edited.body == "Only the body changed"
    assert edited.to.name == "District Officer"


def test_blank_subject_or_body_is_rejected():
    review = DocumentReviewContract(make_draft(), owner_id="citizen-1")

    for kwargs in ({"subject": "   "}, {"body": "   "}):
        try:
            review.edit(actor_id="citizen-1", **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("blank document content must fail")
