from __future__ import annotations

import pytest

from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.submission import (
    CONSENT_PURPOSE,
    SubmissionCapability,
    SubmissionReceipt,
    SubmissionRequest,
)
from src.core.civic_case import CaseStatus, CaseType
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository

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
        consent_id="consent-submission-test",
        subject_id="citizen:submission-test",
        purpose=CONSENT_PURPOSE,
        scope=("email:government",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-09T00:00:00Z",
    )


def _prepared_case() -> tuple[CivicCaseCapability, InMemoryConsentRepository, IdentityContext, str]:
    case_repo = InMemoryCivicCaseRepository()
    case_capability = CivicCaseCapability(case_repo)
    consent_repo = InMemoryConsentRepository()
    consent_repo.save(_consent())
    identity = _identity(CASE_CAPABILITY, "case:write", "case:review", SUBMIT_CAPABILITY)
    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Broken streetlight",
            narrative="The streetlight has not worked for three nights.",
        ),
        identity=identity,
    ).case
    case_capability.add_document(case.case_id, "doc-1", identity=identity)
    case_capability.add_consent(case.case_id, _consent().consent_id, identity=identity)
    case_capability.start_review(case.case_id, identity=identity)
    case_capability.approve(case.case_id, identity=identity)
    return case_capability, consent_repo, identity, case.case_id


class FakeTransport:
    def __init__(self, receipt: SubmissionReceipt | None = None, error: Exception | None = None) -> None:
        self.receipt = receipt or SubmissionReceipt()
        self.error = error
        self.calls = 0

    def send(self, *, case, document_id: str, destination_ref: str) -> SubmissionReceipt:
        self.calls += 1
        if self.error:
            raise self.error
        return self.receipt


def _request(case_id: str) -> SubmissionRequest:
    return SubmissionRequest(
        case_id=case_id,
        document_id="doc-1",
        destination_ref="authority:email:example",
        consent_scope="email:government",
        source_channel="web",
    )


def test_submission_requires_explicit_user_approval() -> None:
    cases, consents, identity, case_id = _prepared_case()
    transport = FakeTransport()
    capability = SubmissionCapability(cases, consents, transport)

    with pytest.raises(PermissionError, match="Explicit user approval"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=False)

    assert transport.calls == 0
    assert cases.get_owned(case_id, identity=identity).status is CaseStatus.READY


def test_submission_requires_matching_consent() -> None:
    cases, _, identity, case_id = _prepared_case()
    consents = InMemoryConsentRepository()
    capability = SubmissionCapability(cases, consents, FakeTransport())

    with pytest.raises(PermissionError, match="Explicit consent"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)


def test_submission_failure_never_claims_success() -> None:
    cases, consents, identity, case_id = _prepared_case()
    transport = FakeTransport(error=RuntimeError("gateway unavailable"))
    capability = SubmissionCapability(cases, consents, transport)

    with pytest.raises(RuntimeError, match="gateway unavailable"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)

    assert cases.get_owned(case_id, identity=identity).status is CaseStatus.SUBMITTING
    assert cases.get_owned(case_id, identity=identity).confirmed_delivery() is False


def test_successful_submission_records_acknowledgement_only_when_transport_confirms() -> None:
    cases, consents, identity, case_id = _prepared_case()
    transport = FakeTransport(SubmissionReceipt(acknowledgement_ref="ack-123", notes="Accepted by destination"))
    capability = SubmissionCapability(cases, consents, transport)

    result = capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)

    assert result.authorization is AuthorizationDecision.ALLOW
    assert result.case.status is CaseStatus.ACKNOWLEDGED
    assert result.case.confirmed_delivery() is True
    assert result.case.events[-2].event_type.value == "submitted"
    assert result.case.events[-1].event_type.value == "acknowledged"
    assert result.case.events[-1].source_ref == "ack-123"


def test_document_generation_does_not_imply_submission() -> None:
    cases, _, identity, case_id = _prepared_case()
    case = cases.get_owned(case_id, identity=identity)
    assert case.document_refs == ["doc-1"]
    assert case.status is CaseStatus.READY
    assert case.confirmed_delivery() is False
