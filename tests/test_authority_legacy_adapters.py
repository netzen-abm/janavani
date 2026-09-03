from src.services.office_service import find_offices
from src.services.search_directory import search_office
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.core.authority import AuthorityContact, AuthorityRecord


def repository() -> InMemoryAuthorityRepository:
    repo = InMemoryAuthorityRepository()
    repo.save(
        AuthorityRecord(
            authority_id="1",
            name="Edathala Panchayat",
            authority_type="Panchayat",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(
                name="Secretary",
                address="Edathala PO",
                email="secretary@example.gov.in",
                role="Secretary",
            ),
        )
    )
    return repo


def test_legacy_office_service_preserves_dict_shape():
    offices = find_offices("Panchayat", "Kochi", repository=repository())
    assert offices == [
        {
            "id": "1",
            "name": "Edathala Panchayat",
            "type": "Panchayat",
            "address": "Edathala PO",
            "city": "Kochi",
            "officer_role": "Secretary",
            "email": "secretary@example.gov.in",
        }
    ]


def test_legacy_directory_search_uses_canonical_authority():
    output = search_office("Panchayat", "Kochi", repository=repository())
    assert "Edathala Panchayat" in output
    assert "secretary@example.gov.in" in output
    assert "ID: 1" in output
