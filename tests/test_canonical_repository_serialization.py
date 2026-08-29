from src.domain.document import Document, DocumentType, PartyRef


def test_document_requires_explicit_user_approval_before_export() -> None:
    document = Document.create(
        document_type=DocumentType.COMPLAINT,
        title="Service complaint",
        language="en",
        subject="Delayed service",
        body="Please investigate the delay.",
        to_party=PartyRef(party_type="office", name="Example Office"),
    )

    assert document.status.value == "draft"
    approved = document.approve()
    assert approved.status.value == "user_approved"
