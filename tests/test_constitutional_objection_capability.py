"""Adversarial tests for the canonical constitutional objection capability."""

import pytest

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.constitutional_objection import ConstitutionalObjectionCapability
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def identity(principal_id="test-principal"):
    principal = Principal(
        principal_id=principal_id,
        interface="test",
        capabilities=frozenset({
            "JNV-CIVIC-COMPLAINT", "case:write", "case:review",
        }),
    )
    return IdentityContext(principal=principal)


def authority_repo():
    contact = AuthorityContact(
        name="Assembly Secretariat",
        address="Official Address",
        email="secretariat@example.gov.in",
        role="Secretariat",
        verified=True,
    )
    authority = AuthorityRecord(
        authority_id="assembly-office",
        name="Assembly Secretariat",
        authority_type="legislative",
        jurisdiction={"state": "Kerala"},
        primary_contact=contact,
        verification_status="VERIFIED",
    )
    return InMemoryAuthorityRepository([authority])


def bill_loader(code):
    if code != "BILL-TEST":
        return None
    return {
        "title": "Test Public Participation Bill",
        "state": "Kerala",
        "constitutional_evaluation": {
            "article_14_analysis": "Test Article 14 analysis",
            "article_19_analysis": "Test Article 19 analysis",
            "article_21_analysis": "Test Article 21 analysis",
            "overall_constitutional_summary": "Test constitutional summary",
        },
    }


def capability(cases):
    return ConstitutionalObjectionCapability(
        case_capability=CivicCaseCapability(cases),
        case_repository=cases,
        authority_repository=authority_repo(),
        bill_profile_loader=bill_loader,
    )


def create_objection_case(cases, principal="test-principal"):
    request = CivicCaseCreateRequest(
        case_type=CaseType.OBJECTION,
        subject="Objection to proposed bill",
        narrative="Citizen's constitutional objection.",
        related_office_id="assembly-office",
    )
    return CivicCaseCapability(cases).create(
        request,
        identity=identity(principal),
        source_channel="test",
    ).case


def test_builds_only_from_owned_case_and_verified_authority():
    cases = InMemoryCivicCaseRepository()
    case = create_objection_case(cases)
    result = capability(cases).build_document(
        case.case_id,
        identity=identity(),
        bill_code="BILL-TEST",
        citizen_comments="The proposed restriction is disproportionate.",
        document_id="doc-objection-1",
    )
    assert result.case_id == case.case_id
    assert result.authority_id == "assembly-office"
    assert result.draft.case_id == case.case_id
    assert result.draft.to.email == "secretariat@example.gov.in"
    assert "The proposed restriction is disproportionate." in result.draft.body


def test_rejects_cross_owner_case():
    cases = InMemoryCivicCaseRepository()
    case = create_objection_case(cases, "owner")
    with pytest.raises(LookupError):
        capability(cases).build_document(
            case.case_id,
            identity=identity("other"),
            bill_code="BILL-TEST",
            citizen_comments="Not my case.",
        )


def test_rejects_non_objection_case():
    cases = InMemoryCivicCaseRepository()
    request = CivicCaseCreateRequest(
        case_type=CaseType.COMPLAINT,
        subject="Complaint",
        narrative="Not an objection.",
        related_office_id="assembly-office",
    )
    case = CivicCaseCapability(cases).create(
        request, identity=identity(), source_channel="test"
    ).case
    with pytest.raises(ValueError, match="not an objection"):
        capability(cases).build_document(
            case.case_id,
            identity=identity(),
            bill_code="BILL-TEST",
            citizen_comments="Wrong case type.",
        )


def test_rejects_unknown_bill_profile():
    cases = InMemoryCivicCaseRepository()
    case = create_objection_case(cases)
    with pytest.raises(LookupError, match="bill index code"):
        capability(cases).build_document(
            case.case_id,
            identity=identity(),
            bill_code="UNKNOWN",
            citizen_comments="There is a concern.",
        )


def test_rejects_unverified_authority():
    cases = InMemoryCivicCaseRepository()
    contact = AuthorityContact(
        name="Unverified Contact",
        address="Unknown",
        email="unknown@example.gov.in",
        verified=False,
    )
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="unverified",
            name="Unverified Secretariat",
            authority_type="legislative",
            primary_contact=contact,
            verification_status="UNVERIFIED",
        )
    ])
    request = CivicCaseCreateRequest(
        case_type=CaseType.OBJECTION,
        subject="Objection",
        narrative="Must fail closed.",
        related_office_id="unverified",
    )
    case = CivicCaseCapability(cases).create(
        request, identity=identity(), source_channel="test"
    ).case
    action = ConstitutionalObjectionCapability(
        case_capability=CivicCaseCapability(cases),
        case_repository=cases,
        authority_repository=authorities,
        bill_profile_loader=bill_loader,
    )
    with pytest.raises(ValueError, match="not verified"):
        action.build_document(
            case.case_id,
            identity=identity(),
            bill_code="BILL-TEST",
            citizen_comments="Must fail closed.",
        )
