from __future__ import annotations

from src.capabilities.submission import SubmissionCapability, SubmissionRequest
from src.delivery.contract import DeliveryReceipt
from src.storage.repositories.submission import InMemorySubmissionRepository

from tests.test_submission_capability import FakeDeliveryResolver, _prepared_case


class CapturingDeliveryTransport:
    def __init__(self) -> None:
        self.requests = []

    def deliver(self, request):
        self.requests.append(request)
        return DeliveryReceipt(external_reference="transport-ref")


def test_submission_propagates_stable_idempotency_key_to_delivery_transport() -> None:
    cases, consents, identity, case_id = _prepared_case()
    transport = CapturingDeliveryTransport()
    capability = SubmissionCapability(
        cases,
        consents,
        submission_repository=InMemorySubmissionRepository(),
        delivery_transport=transport,
        artifact_resolver=FakeDeliveryResolver(),
    )

    request = SubmissionRequest(
        case_id=case_id,
        document_id="doc-1",
        destination_ref="authority:email:example",
        consent_scope="email:government",
        source_channel="web",
        artifact_id="artifact-1",
        idempotency_key="stable-submit-key",
    )
    capability.submit(request, identity=identity, explicit_user_approval=True)

    assert len(transport.requests) == 1
    delivery_request = transport.requests[0]
    assert delivery_request.submission_id
    assert delivery_request.idempotency_key == "stable-submit-key"
    assert delivery_request.case_id == case_id
    assert delivery_request.document_id == "doc-1"


def test_delivery_request_rejects_missing_or_blank_idempotency_key() -> None:
    from src.delivery.contract import DeliveryArtifact, DeliveryRequest

    artifact = DeliveryArtifact(
        artifact_id="artifact-1",
        document_id="doc-1",
        case_id="case-1",
        format="pdf",
        content=b"approved",
        content_sha256="a" * 64,
        media_type="application/pdf",
    )
    for key in ("", "   "):
        try:
            DeliveryRequest(
                submission_id="submission-1",
                idempotency_key=key,
                case_id="case-1",
                document_id="doc-1",
                destination_ref="authority:test",
                channel="web",
                artifact=artifact,
            )
        except ValueError as exc:
            assert "idempotency_key" in str(exc)
        else:
            raise AssertionError("blank idempotency key must be rejected")
