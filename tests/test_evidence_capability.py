"""Focused tests for the shared Evidence capability boundary."""

import pytest

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.evidence import EvidenceCapability, EvidenceCreateRequest
from src.core.civic_case import CaseType
from src.core.evidence import EvidenceSource
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository


def identity(principal_id: str = "owner", *, evidence: bool = True) -> IdentityContext:
    capabilities = {"JNV-CIVIC-COMPLAINT", "case:write", "case:evidence"} if evidence else {"JNV-CIVIC-COMPLAINT", "case:write"}
    return IdentityContext(principal=Principal(principal_id=principal_id, interface="test", capabilities=frozenset(capabilities)))


def create_case(repo):
    return CivicCaseCapability(repo).create(
        CivicCaseCreateRequest(case_type=CaseType.COMPLAINT, subject="Water issue", narrative="Water service failed."),
        identity=identity(), source_channel="test",
    ).case


def test_register_preserves_canonical_hash_and_provenance() -> None:
    cases = InMemoryCivicCaseRepository()
    evidence_repo = InMemoryEvidenceRepository()
    evidence = EvidenceCapability(evidence_repo, CivicCaseCapability(cases)).register(
        EvidenceCreateRequest(
            evidence_type="PHOTO", storage_ref="local://evidence/photo-1", sha256="A" * 64,
            received_at="2026-09-09T00:00:00Z", captured_at="2026-09-08T12:00:00Z",
            provenance=(EvidenceSource(source_id="device-1", source_type="LOCAL_DEVICE"),),
        ), identity=identity(),
    )
    assert evidence.sha256 == "a" * 64
    assert evidence_repo.get(evidence.evidence_id).provenance[0].source_type == "LOCAL_DEVICE"
    assert evidence_repo.get(evidence.evidence_id).storage_ref == "local://evidence/photo-1"


def test_attach_requires_registered_evidence_and_owned_case() -> None:
    cases = InMemoryCivicCaseRepository()
    evidence_repo = InMemoryEvidenceRepository()
    capability = EvidenceCapability(evidence_repo, CivicCaseCapability(cases))
    case = create_case(cases)
    evidence = capability.register(EvidenceCreateRequest("DOCUMENT", "local://document/1", "b" * 64, "2026-09-09T00:00:00Z"), identity=identity())
    result = capability.attach(case.case_id, evidence.evidence_id, identity=identity(), source_channel="test")
    assert evidence.evidence_id in result.case.evidence_refs
    with pytest.raises(LookupError):
        capability.attach(case.case_id, "missing", identity=identity())
    with pytest.raises(LookupError):
        capability.attach(case.case_id, evidence.evidence_id, identity=identity("other"))


def test_registration_denies_missing_evidence_capability() -> None:
    capability = EvidenceCapability(InMemoryEvidenceRepository(), CivicCaseCapability(InMemoryCivicCaseRepository()))
    with pytest.raises(PermissionError):
        capability.register(EvidenceCreateRequest("DOCUMENT", "local://document/1", "c" * 64, "2026-09-09T00:00:00Z"), identity=identity(evidence=False))


def test_get_for_case_is_owner_scoped() -> None:
    cases = InMemoryCivicCaseRepository()
    evidence_repo = InMemoryEvidenceRepository()
    capability = EvidenceCapability(evidence_repo, CivicCaseCapability(cases))
    case = create_case(cases)
    evidence = capability.register(EvidenceCreateRequest("DOCUMENT", "local://document/1", "d" * 64, "2026-09-09T00:00:00Z"), identity=identity())
    capability.attach(case.case_id, evidence.evidence_id, identity=identity())
    assert capability.get_for_case(case.case_id, identity=identity())[0].evidence_id == evidence.evidence_id
    with pytest.raises(LookupError):
        capability.get_for_case(case.case_id, identity=identity("other"))


def test_execution_envelope_is_validated_and_propagated_to_case() -> None:
    cases = InMemoryCivicCaseRepository()
    evidence_repo = InMemoryEvidenceRepository()
    capability = EvidenceCapability(evidence_repo, CivicCaseCapability(cases))
    case = create_case(cases)
    evidence = capability.register(EvidenceCreateRequest("PHOTO", "local://photo/1", "e" * 64, "2026-09-09T00:00:00Z"), identity=identity())
    context = CapabilityExecutionContext.for_capability(identity(), capability_id="case:evidence", action="evidence:attach", surface="telegram", resource_id=case.case_id)
    result = capability.attach(case.case_id, evidence.evidence_id, identity=identity(), execution_context=context)
    assert evidence.evidence_id in result.case.evidence_refs


def test_execution_envelope_rejects_wrong_identity() -> None:
    capability = EvidenceCapability(InMemoryEvidenceRepository(), CivicCaseCapability(InMemoryCivicCaseRepository()))
    context = CapabilityExecutionContext.for_capability(identity("owner"), capability_id="case:evidence", action="evidence:register", surface="webapp")
    with pytest.raises(PermissionError):
        capability.register(EvidenceCreateRequest("DOCUMENT", "local://document/2", "f" * 64, "2026-09-09T00:00:00Z"), identity=identity("other"), execution_context=context)
