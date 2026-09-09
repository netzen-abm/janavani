"""Contract tests for the shared Authority capability."""

import pytest

from src.capabilities.authority import AuthorityCapability, AuthorityLookupRequest
from src.core.authority import AuthorityContact, AuthorityRecord
from src.storage.repositories.authority import InMemoryAuthorityRepository


def records() -> InMemoryAuthorityRepository:
    return InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-1",
            name="District Office",
            authority_type="district",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(
                name="District Officer",
                address="Official Address",
                email="office@example.gov.in",
            ),
            verification_status="VERIFIED",
        ),
        AuthorityRecord(
            authority_id="office-2",
            name="Unverified Office",
            authority_type="district",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(name="Unknown", address="Unknown"),
            verification_status="UNVERIFIED",
        ),
    ])


def test_authority_capability_resolves_by_id() -> None:
    capability = AuthorityCapability(records())
    authority = capability.get("office-1")
    assert authority is not None
    assert authority.name == "District Office"


def test_authority_capability_search_is_provider_neutral() -> None:
    capability = AuthorityCapability(records())
    result = capability.search(AuthorityLookupRequest(authority_type="district", city="Kochi"))
    assert [item.authority_id for item in result] == ["office-1", "office-2"]


def test_authority_capability_requires_verified_destination() -> None:
    capability = AuthorityCapability(records())
    destination = capability.require_verified_destination("office-1")
    assert destination.email == "office@example.gov.in"


def test_authority_capability_rejects_unverified_destination() -> None:
    capability = AuthorityCapability(records())
    with pytest.raises(ValueError, match="not verified"):
        capability.require_verified_destination("office-2")


def test_authority_capability_rejects_missing_authority() -> None:
    capability = AuthorityCapability(records())
    with pytest.raises(LookupError, match="Authority not found"):
        capability.require_verified_destination("missing")
