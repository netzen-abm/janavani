from pathlib import Path

from src.core.authority import AuthorityContact, AuthorityRecord
from src.documents.generate_pdf import generate_pdf_from_complaint
from src.storage.repositories.authority import InMemoryAuthorityRepository


def test_legacy_pdf_uses_authority_repository(tmp_path: Path) -> None:
    repository = InMemoryAuthorityRepository(
        [
            AuthorityRecord(
                authority_id="7",
                name="Canonical Office",
                authority_type="Panchayat",
                jurisdiction={"city": "Kochi"},
                primary_contact=AuthorityContact(
                    name="Secretary",
                    address="Verified Address",
                    email="secretary@example.gov.in",
                    role="Secretary",
                ),
            )
        ]
    )
    complaint = {
        "complaint_id": "JV-7",
        "office_id": "7",
        "date": "2026-09-04",
        "user": {"name": "Citizen", "address": "Citizen Address"},
        "issue": "Service issue",
    }

    output = generate_pdf_from_complaint(
        complaint,
        authority_repository=repository,
        output_dir=tmp_path,
    )

    assert Path(output).exists()
