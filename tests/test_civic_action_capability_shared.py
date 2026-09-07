"""Adversarial contract tests for the shared civic action capability."""
from dataclasses import dataclass

import pytest

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.core.evidence import EvidenceObject
from src.identity.context import IdentityContext, IdentityMode
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository


def identity(principal_id: str = "test-principal") -> IdentityContext:
    return IdentityContext(
        principal=Principal(principal_id=principal_id),
        mode=IdentityMode.ANONYMOUS,
        interface="test",
        authentication_method="NONE",
        capabilities={"JNV-CIVIC-COMPLAINT"},
    )


def authority_repo() -> InMemoryAuthorityRepository:
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
                role="District Officer",
                verified=True,
            ),
            verification_status="VERIFIED",
        )
    ])


def capability(case_repo, evidence_repo=None):
    case_capability = CivicCaseCapability(case_repo)
    return CivicActionCapability(
        case_capability=case_capability,
        case_repository=case_repo,
        authority_repository=authority_repo(),
        evidence_repository=evidence_repo,
    )


def test_shared_capability_uses_owned_case_and_verified_destination() -> None:
    cases = InMemoryCivicCaseRepository()
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Water issue",
            narrative="Water service has failed.",
            related_office_id="office-1",
        ),
        identity=identity(),
        source_channel="test",
    ).case

    result = capability(cases).build_document(case.case_id, identity=identity(), document_id="doc-1", date="2026-09-07")

    assert result.draft.case_id == case.case_id
    assert result.authority_id == "office-1"
    assert result.draft.to.email == "office@example.gov.in"


def test_shared_capability_rejects_cross_owner_access() -> None:
    cases = InMemoryCivicCaseRepository()
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Water issue",
            narrative="Water service has failed.",
            related_office_id="office-1",
        ),
        identity=identity("owner"),
        source_channel="test",
    ).case

    with pytest.raises(LookupError):
        capability(cases).build_document(case.case_id, identity=identity("other"))


def test_shared_capability_rejects_missing_evidence() -> None:
    cases = InMemoryCivicCaseRepository()
    evidence = InMemoryEvidenceRepository()
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Evidence issue",
            narrative="Evidence reference is not resolvable.",
            related_office_id="office-1",
        ),
        identity=identity(),
        source_channel="test",
    ).case
    case.evidence_refs.append("missing-evidence")
    cases.save(case)

    with pytest.raises(ValueError, match="missing evidence"):
        capability(cases, evidence).build_document(case.case_id, identity=identity())


def test_shared_capability_fails_closed_without_authority_destination() -> None:
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(authority_id="office-2", name="No Destination", authority_type="office")
    ])
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Destination issue",
            narrative="Destination is absent.",
            related_office_id="office-2",
        ),
        identity=identity(),
        source_channel="test",
    ).case
    action = CivicActionCapability(
        case_capability=CivicCaseCapability(cases),
        case_repository=cases,
        authority_repository=authorities,
    )

    with pytest.raises(ValueError, match="destination"):
        action.build_document(case.case_id, identity=identity())
