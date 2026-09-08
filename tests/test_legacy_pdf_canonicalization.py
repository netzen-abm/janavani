from pathlib import Path

from src.core.authority import AuthorityContact, AuthorityRecord
from src.documents.document_contract import DocumentDraft, DocumentFormat, DocumentParty
from src.documents.renderers import render_document
from src.storage.repositories.authority import InMemoryAuthorityRepository


def test_canonical_pdf_renderer_uses_verified_authority_contract(tmp_path: Path) -> None:
    repository = InMemoryAuthorityRepository(
        [
            AuthorityRecord(
                authority_id="7",
                name="Canonical Office",
                authority_type="Panchayat",
                jurisdiction={"city": "Kochi"},
                verification_status="VERIFIED",
                primary_contact=AuthorityContact(
                    name="Secretary",
                    address="Verified Address",
                    email="secretary@example.gov.in",
                    role="Secretary",
                    verified=True,
                ),
            )
        ]
    )
    authority = repository.get("7")
    assert authority is not None
    assert authority.verified
    contact = authority.primary_contact
    assert contact is not None

    draft = DocumentDraft(
        document_id="JV-7",
        document_type="complaint",
        case_id="case-7",
        date="2026-09-04",
        subject=f"Complaint regarding {authority.name}",
        body="Service issue",
        to=DocumentParty(
            name=contact.name,
            address=contact.address,
            email=contact.email,
            role=contact.role,
        ),
        sender=DocumentParty(
            name="Citizen",
            address="Citizen Address",
            role="Citizen",
        ),
    )

    output = render_document(draft, DocumentFormat.PDF, tmp_path)
    assert Path(output).exists()
