"""Adversarial contract tests for the shared civic action capability."""

import pytest

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.core.evidence import EvidenceObject
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository


def identity(principal_id: str = "test-principal") -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            interface="test",
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}),
        )
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


def action_capability(case_repo, evidence_repo=None, authorities=None):
    return CivicActionCapability(
        case_capability=CivicCaseCapability(case_repo),
        case_repository=case_repo,
        authority_repository=authorities or authority_repo(),
        evidence_repository=evidence_repo,
    )


def create_case(cases, principal="test-principal"):
    return CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Water issue",
            narrative="Water service has failed.",
            related_office_id="office-1",
        ),
        identity=identity(principal),
        source_channel="test",
    ).case


def test_shared_capability_uses_owned_case_and_verified_destination() -> None:
    cases = InMemoryCivicCaseRepository()
    case = create_case(cases)
    result = action_capability(cases).build_document(
        case.case_id, identity=identity(), document_id="doc-1", date="2026-09-07"
    )
    assert result.draft.case_id == case.case_id
    assert result.authority_id == "office-1"
    assert result.draft.to.email == "office@example.gov.in"


def test_shared_capability_rejects_cross_owner_access() -> None:
    cases = InMemoryCivicCaseRepository()
    case = create_case(cases, "owner")
    with pytest.raises(LookupError):
        action_capability(cases).build_document(case.case_id, identity=identity("other"))


def test_shared_capability_rejects_missing_evidence() -> None:
    cases = InMemoryCivicCaseRepository()
    evidence = InMemoryEvidenceRepository()
    case = create_case(cases)
    case.evidence_refs.append("missing-evidence")
    cases.save(case)
    with pytest.raises(ValueError, match="missing evidence"):
        action_capability(cases, evidence).build_document(case.case_id, identity=identity())


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
    action = action_capability(cases, authorities=authorities)
    with pytest.raises(ValueError, match="destination"):
        action.build_document(case.case_id, identity=identity())


def test_evidence_repository_normalizes_sha256() -> None:
    evidence = InMemoryEvidenceRepository()
    evidence.save(EvidenceObject(
        evidence_id="evidence-1",
        evidence_type="DOCUMENT",
        storage_ref="object://evidence-1",
        sha256="A" * 64,
        received_at="2026-09-07T00:00:00Z",
    ))
    assert evidence.get("evidence-1").sha256 == "a" * 64
