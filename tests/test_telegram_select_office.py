import pytest

from src.conversation.steps.select_office import _authority_to_session_record
from src.domain.authority import Authority, AuthoritySource


def test_authority_to_session_record_preserves_provenance() -> None:
    authority = Authority.create(
        "Revenue Office",
        "government_office",
        jurisdiction={"city": "Bengaluru"},
        postal_addresses=["District Complex"],
        contact_points=["080-1234"],
        official_urls=["https://example.gov.in"],
        source_refs=[
            AuthoritySource(
                source_id="office-directory-csv",
                source_type="OTHER",
                uri="database/offices.csv",
            )
        ],
    )

    record = _authority_to_session_record(authority)

    assert record["authority_id"] == authority.authority_id
    assert record["id"] == authority.authority_id
    assert record["name"] == "Revenue Office"
    assert record["city"] == "Bengaluru"
    assert record["address"] == "District Complex"
    assert record["verification_status"] == "unverified"
    assert record["source_refs"] == ["office-directory-csv"]


def test_authority_to_session_record_handles_missing_optional_contacts() -> None:
    authority = Authority.create(
        "Revenue Office",
        "government_office",
        jurisdiction={"city": "Bengaluru"},
    )

    record = _authority_to_session_record(authority)

    assert record["address"] == ""
    assert record["phone"] == ""
    assert record["website"] == ""
    assert record["source_refs"] == []
