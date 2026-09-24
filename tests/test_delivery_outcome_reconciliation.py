"""Provider-neutral delivery outcome and reconciliation boundary tests."""
from __future__ import annotations

import pytest

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.submission import SubmissionCapability, SubmissionOutcomeUnknown, SubmissionRequest
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.civic_case import CaseStatus, CaseType
from src.delivery.contract import DeliveryArtifact, DeliveryOutcome, DeliveryReceipt, DeliveryTransportError
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository
from src.storage.repositories.submission import InMemorySubmissionRepository

CASE_CAPABILITY = "JNV-CIVIC-COMPLAINT"
SUBMIT_CAPABILITY = "case:submit"


def _identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:delivery-outcome-test",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({CASE_CAPABILITY, "case:write", "case:review", SUBMIT_CAPABILITY, "case:evidence"}),
        ),
        request_id="delivery-outcome-request",
    )


def _prepared() -> tuple[CivicCaseCapability, InMemoryConsentRepository, InMemorySubmissionRepository, IdentityContext, str]:
    cases = CivicCaseCapability(InMemoryCivicCaseRepository())
    consents = InMemoryConsentRepository()
    identity = _identity()
    consents.save(Consent(
        consent_id="consent-delivery-outcome", subject_id=identity.principal.principal_id,
        purpose="case_submission", scope=("email:government",), grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED, created_at="2026-09-13T00:00:00Z",
    ))
    case = cases.create(
        CivicCaseCreateRequest(case_type=CaseType.COMPLAINT, subject="Road repair", narrative="Road remains damaged."),
        identity=identity,
    ).case
    cases.start_review(case.case_id, identity=identity)
    cases.add_consent(case.case_id, "consent-delivery-outcome", identity=identity)
    cases.approve(case.case_id, identity=identity)
    case.document_refs.append("doc-delivery-outcome")
    cases.save_owned(case, identity=identity)
    return cases, consents, InMemorySubmissionRepository(), identity, case.case_id


class Resolver:
    def resolve(self, *, artifact_id: str, case_id: str, document_id: str) -> DeliveryArtifact:
        return DeliveryArtifact(
            artifact_id=artifact_id, document_id=document_id, case_id=case_id,
            format="pdf", content=b"approved", content_sha256="a" * 64, media_type="application/pdf",
        )


class UnknownReceiptTransport:
    def deliver(self, request) -> DeliveryReceipt:
        return DeliveryReceipt(outcome=DeliveryOutcome.UNKNOWN, transport_reference="attempt-1")


class FailedReceiptTransport:
    def deliver(self, request) -> DeliveryReceipt:
        return DeliveryReceipt(outcome=DeliveryOutcome.FAILED, transport_reference="attempt-2")


class AmbiguousExceptionTransport:
    def deliver(self, request) -> DeliveryReceipt:
        raise RuntimeError("connection reset after send")


class ExplicitFailedExceptionTransport:
    def deliver(self, request) -> DeliveryReceipt:
        raise DeliveryTransportError("destination rejected request", outcome=DeliveryOutcome.FAILED)


def _request(case_id: str, key: str = "stable-delivery-key") -> SubmissionRequest:
    return SubmissionRequest(
        case_id=case_id, document_id="doc-delivery-outcome", destination_ref="authority:email:test",
        consent_scope="email:government", source_channel="web", artifact_id="artifact-delivery-outcome",
        idempotency_key=key,
        external_channel_id="channel-verified",
    )


def test_unknown_receipt_is_persisted_and_never_claimed_submitted() -> None:
    cases, consents, submissions, identity, case_id = _prepared()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=UnknownReceiptTransport(), artifact_resolver=Resolver(),
    )
    with pytest.raises(SubmissionOutcomeUnknown, match="reconciliation"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "unknown"
    assert record.retry_count == 0
    assert cases.get_owned(case_id, identity=identity).status is CaseStatus.SUBMITTING


def test_ambiguous_transport_exception_becomes_unknown_not_failed() -> None:
    cases, consents, submissions, identity, case_id = _prepared()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=AmbiguousExceptionTransport(), artifact_resolver=Resolver(),
    )
    with pytest.raises(SubmissionOutcomeUnknown):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "unknown"
    assert record.retry_count == 0


def test_explicit_failed_receipt_is_retryable_failure() -> None:
    cases, consents, submissions, identity, case_id = _prepared()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=FailedReceiptTransport(), artifact_resolver=Resolver(),
    )
    with pytest.raises(RuntimeError, match="reported failure"):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "failed"
    assert record.retry_count == 1


def test_transport_error_can_explicitly_report_failed() -> None:
    cases, consents, submissions, identity, case_id = _prepared()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=ExplicitFailedExceptionTransport(), artifact_resolver=Resolver(),
    )
    with pytest.raises(DeliveryTransportError):
        capability.submit(_request(case_id), identity=identity, explicit_user_approval=True)
    record = submissions.list_for_case(case_id)[0]
    assert record.state == "failed"
    assert record.retry_count == 1


def test_delivery_receipt_default_remains_submitted_for_legacy_adapters() -> None:
    assert DeliveryReceipt().outcome is DeliveryOutcome.SUBMITTED


class CountingSubmittedTransport:
    def __init__(self) -> None:
        self.calls = 0

    def deliver(self, request) -> DeliveryReceipt:
        self.calls += 1
        return DeliveryReceipt(
            outcome=DeliveryOutcome.SUBMITTED,
            transport_reference=f"attempt-{self.calls}",
        )


def test_successful_submission_replay_does_not_redeliver():
    cases, consents, submissions, identity, case_id = _prepared()
    transport = CountingSubmittedTransport()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=transport, artifact_resolver=Resolver(),
    )
    request = _request(case_id, key="replay-safe-key")

    first = capability.submit(request, identity=identity, explicit_user_approval=True)
    second = capability.submit(request, identity=identity, explicit_user_approval=True)

    assert first.case.status is CaseStatus.SUBMITTED
    assert second.case.status is CaseStatus.SUBMITTED
    assert transport.calls == 1
    records = submissions.list_for_case(case_id)
    assert len([record for record in records if record.idempotency_key == "replay-safe-key"]) == 1


class BlockingSubmittedTransport:
    def __init__(self) -> None:
        from threading import Event, Lock
        self.started = Event()
        self.release = Event()
        self._lock = Lock()
        self.calls = 0

    def deliver(self, request) -> DeliveryReceipt:
        with self._lock:
            self.calls += 1
            self.started.set()
        self.release.wait(timeout=5)
        return DeliveryReceipt(outcome=DeliveryOutcome.SUBMITTED, transport_reference="concurrent-attempt")


def test_concurrent_submission_reserves_idempotency_before_external_delivery():
    from concurrent.futures import ThreadPoolExecutor
    from src.storage.repositories.submission_case_transaction import SubmissionCaseConcurrencyError

    cases, consents, submissions, identity, case_id = _prepared()
    transport = BlockingSubmittedTransport()
    capability = SubmissionCapability(
        cases, consents, submission_repository=submissions,
        delivery_transport=transport, artifact_resolver=Resolver(),
    )
    request = _request(case_id, key="concurrent-safe-key")

    def invoke():
        return capability.submit(request, identity=identity, explicit_user_approval=True)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(invoke)
        assert transport.started.wait(timeout=5)
        second_future = executor.submit(invoke)
        second_error = None
        try:
            second_future.result(timeout=5)
        except Exception as exc:
            second_error = exc
        transport.release.set()
        first = first_future.result(timeout=5)

    assert first.case.status is CaseStatus.SUBMITTED
    assert isinstance(second_error, (SubmissionCaseConcurrencyError, RuntimeError))
    assert transport.calls == 1
    records = submissions.list_for_case(case_id)
    assert len([record for record in records if record.idempotency_key == "concurrent-safe-key"]) == 1
