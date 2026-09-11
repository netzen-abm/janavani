"""Submission capability tests covering authorization, consent, delivery, and acknowledgement evidence."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.submission import (
    ACKNOWLEDGEMENT_EVIDENCE_TYPE,
    CONSENT_PURPOSE,
    SubmissionCapability,
    SubmissionReceipt,
    SubmissionRequest,
)
from src.core.civic_case import CaseStatus, CaseType
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.evidence import EvidenceObject
from src.delivery.contract import DeliveryArtifact, DeliveryReceipt
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.submission import InMemorySubmissionRepository

CASE_CAPABILITY = "JNV-CIVIC-COMPLAINT"
SUBMIT_CAPABILITY = "case:submit"


def _identity(*capabilities: str) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:submission-test",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset(capabilities),
        ),
        request_id="submission-request-test",
    )


def _consent() -> Consent:
    return Consent(
        consent_id="consent-1",
        subject_id="citizen:submission-test",
        purpose=CONSENT_PURPOSE,
        scope=("email:government",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-10T00:00:00Z",
    )


def _prepared_case() -> tuple[CivicCaseCapability, InMemoryConsentRepository, IdentityContext, str]:
    case_repo = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(case_repo)
    consent_repo = InMemoryConsentRepository()
    consent_repo.save(_consent())
    identity = _identity(CASE_CAPABILITY, "case:write", "case:review", SUBMIT_CAPABILITY, "case:evidence")
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Streetlight repair",
            narrative="Streetlight remains broken.",
        ),
        identity=identity,
    ).case
    case_capability.start_review(case.case_id, identity=identity)
    case_capability.add_consent(case.case_id, "consent-1", identity=identity)
    case_capability.approve(case.case_id, identity=identity)
    case.document_refs.append("doc-1")
    case_capability.save_owned(case, identity=identity)
    return case_capability, consent_repo, identity, case.case_id


@dataclass
class FakeTransport:
    receipt: SubmissionReceipt = SubmissionReceipt()
    error: Exception | None = None
    calls: int = 0

    def send(self, *, case, document_id: str, destination_ref: str) -> SubmissionReceipt:
        self.calls += 1
        if self.error:
            raise self.error
        return self.receipt


class FakeDeliveryResolver:
    def resolve(self, *, artifact_id: str, case_id: str, document_id: str) -> DeliveryArtifact:
        return DeliveryArtifact(
            artifact_id=artifact_id,
            document_id=document_id,
            case_id=case_id,
            format="pdf",
            content=b"approved document",
            content_sha256="a" * 64,
            media_type="application/pdf",
        )


class FakeDeliveryTransport:
    def __init__(self, receipt: DeliveryReceipt | None = None) -> None:
        self.receipt = receipt or DeliveryReceipt()
        self.calls = 0

    def deliver(self, request) -> DeliveryReceipt:
        self.calls += 1
        return self.receipt


def _request(case_id: str, *, artifact_id: str | None = None) -> SubmissionRequest:
    return SubmissionRequest(
        case_id=case_id,
        document_id="doc-1",
        destination_ref="authority:email:example",
        consent_scope="email:government",
        source_channel="web",
        artifact_id=artifact_id,
    )


def _ack_evidence(case_id: str) -> EvidenceObject:
    return EvidenceObject(
        evidence_id="evidence-ack-1",
        evidence_type=ACKNOWLEDGEMENT_EVIDENCE_TYPE,
        storage_ref="evidence://ack-1",
        sha256="b" * 64,
        received_at="2026-09-10T00:00:00Z",
        source_description="Destination acknowledgement evidence",
        status="ACTIVE",
    )


def test_submission_requires_explicit_user_approval() -> None:
    cases, consents, identity, case_id = _prepared_case()
    capability = SubmissionCapability(cases, consents, FakeTransport(), InMemorySubmissionRepository())
    with pytest.raises(PermissionError, match="Explicit user approval"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=False)


def test_submission_requires_matching_consent() -> None:
    cases, consents, identity, case_id = _prepared_case()
    consents.clear()
    capability = SubmissionCapability(cases, consents, FakeTransport(), InMemorySubmissionRepository())
    with pytest.raises(PermissionError):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)


def test_submission_failure_persists_failed_delivery_without_claiming_success() -> None:
    cases, consents, identity, case_id = _prepared_case()
    submissions = InMemorySubmissionRepository()
    capability = SubmissionCapability(
        cases, consents, FakeTransport(error=RuntimeError("transport down")), submissions,
    )
    with pytest.raises(RuntimeError):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    assert submissions.list_for_case(case_id)[0].state == "failed"
    assert cases.get_owned(case_id, identity=identity).confirmed_delivery() is False


def test_delivery_transport_requires_approved_artifact() -> None:
    cases, consents, identity, case_id = _prepared_case()
    submissions = InMemorySubmissionRepository()
    transport = FakeDeliveryTransport()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=transport, artifact_resolver=FakeDeliveryResolver(),
    )
    with pytest.raises(ValueError, match="approved artifact"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    assert transport.calls == 0


def test_delivery_submission_requires_independent_acknowledgement_evidence() -> None:
    cases, consents, identity, case_id = _prepared_case()
    submissions = InMemorySubmissionRepository()
    evidence = InMemoryEvidenceRepository()
    evidence_obj = _ack_evidence(case_id)
    evidence.save(evidence_obj)
    cases.add_evidence(case_id, evidence_obj.evidence_id, identity=identity)
    transport = FakeDeliveryTransport(DeliveryReceipt(
        external_reference="ext-123",
        transport_reference="transport-123",
        acknowledgement_evidence_ref=evidence_obj.evidence_id,
        notes="Accepted by destination",
    ))
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=transport, artifact_resolver=FakeDeliveryResolver(),
        evidence_repository=evidence,
    )
    result = capability.submit(
        _request(case_id, artifact_id="artifact-1"), identity=identity, explicit_user_approval=True,
    )
    assert transport.calls == 1
    assert result.case.status is CaseStatus.ACKNOWLEDGED
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "acknowledged"
    assert record.external_reference == "ext-123"
    assert record.ack_ref == evidence_obj.evidence_id
    assert record.acknowledged_at is not None
    assert result.case.events[-1].source_ref == evidence_obj.evidence_id


def test_delivery_without_acknowledgement_evidence_stays_submitted() -> None:
    cases, consents, identity, case_id = _prepared_case()
    submissions = InMemorySubmissionRepository()
    evidence = InMemoryEvidenceRepository()
    transport = FakeDeliveryTransport(DeliveryReceipt(external_reference="ext-456"))
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=transport, artifact_resolver=FakeDeliveryResolver(),
        evidence_repository=evidence,
    )
    result = capability.submit(
        _request(case_id, artifact_id="artifact-2"), identity=identity, explicit_user_approval=True,
    )
    assert result.case.status is CaseStatus.SUBMITTED
    assert result.case.confirmed_delivery() is False
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "submitted"
    assert record.external_reference == "ext-456"
    assert record.ack_ref is None


def test_legacy_transport_ack_reference_does_not_imply_acknowledgement() -> None:
    cases, consents, identity, case_id = _prepared_case()
    submissions = InMemorySubmissionRepository()
    transport = FakeTransport(SubmissionReceipt(acknowledgement_ref="ack-legacy"))
    capability = SubmissionCapability(cases, consents, transport, submissions)
    result = capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    assert result.case.status is CaseStatus.SUBMITTED
    assert result.case.confirmed_delivery() is False
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "submitted"
    assert record.external_reference == "ack-legacy"
    assert record.ack_ref is None


def test_acknowledge_with_evidence_requires_attached_evidence() -> None:
    cases, consents, identity, case_id = _prepared_case()
    submissions = InMemorySubmissionRepository()
    evidence = InMemoryEvidenceRepository()
    transport = FakeTransport()
    capability = SubmissionCapability(cases, consents, transport, submissions, evidence_repository=evidence)
    capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    evidence.save(_ack_evidence(case_id))
    with pytest.raises(PermissionError, match="not attached"):
        capability.acknowledge_with_evidence(
            submissions.list_for_case(case_id)[0].submission_id,
            evidence_id="evidence-ack-1", identity=identity,
        )


def test_document_generation_does_not_imply_submission() -> None:
    cases, _, identity, case_id = _prepared_case()
    case = cases.get_owned(case_id, identity=identity)
    assert case.status is CaseStatus.READY
    assert case.confirmed_delivery() is False
