from datetime import datetime, timezone

from src.domain.authority import Authority, AuthoritySource
from src.domain.case import Case
from src.domain.consent import Consent
from src.domain.document import Document, DocumentStatus, DocumentType, PartyRef
from src.domain.evidence import Evidence, EvidenceKind
from src.domain.submission import Submission, SubmissionStatus


def test_case_contract_contains_durable_relationships_and_events() -> None:
    case = Case(issue="Broken civic service")
    case.attach_evidence("EVD-1")
    case.add_event("case.created", actor="test")

    assert case.id
    assert case.issue == "Broken civic service"
    assert case.evidence_ids == ["EVD-1"]
    assert case.events[-1].event_type == "case.created"


def test_evidence_contract_preserves_provenance() -> None:
    evidence = Evidence.create(
        "CASE-1",
        EvidenceKind.DOCUMENT,
        "Order copy",
        "citizen",
        content_ref="blob://evidence/1",
        provenance=["official-order-ref"],
    )

    verified = evidence.verify()

    assert verified.evidence_id == evidence.evidence_id
    assert verified.status.value == "verified"
    assert verified.provenance == ["official-order-ref"]


def test_authority_verified_state_requires_source() -> None:
    source = AuthoritySource(
        source_id="SRC-1",
        source_type="official_web",
        uri="https://example.gov/office",
        publisher="Example Government",
    )
    authority = Authority.create(
        "Example Office",
        "government_office",
        source_refs=[source],
    ).verify(verified_at=datetime.now(timezone.utc))

    assert authority.verification_status.value == "verified"
    assert authority.source_refs[0].source_id == "SRC-1"


def test_consent_is_purpose_bound_and_time_aware() -> None:
    consent = Consent.grant(
        "CASE-1",
        "CAP-SUBMIT",
        "Submit civic representation",
        scope=["case", "document"],
        data_categories=["personal"],
        source_channel="web",
    )

    assert consent.is_active()
    assert consent.capability_id == "CAP-SUBMIT"
    assert consent.purpose == "Submit civic representation"


def test_document_requires_explicit_user_approval_before_export() -> None:
    document = Document.create(
        document_type=DocumentType.COMPLAINT,
        title="Service complaint",
        language="en",
        subject="Delayed service",
        body="Please investigate the delay.",
        to=PartyRef(name="Example Office"),
    )

    assert document.status == DocumentStatus.DRAFT
    document.approve()
    assert document.status == DocumentStatus.USER_APPROVED


def test_submission_state_machine_requires_provider_reference_for_delivery() -> None:
    submission = Submission(case_id="CASE-1", destination_ref="AUTH-1")
    submission.transition(SubmissionStatus.QUEUED)
    submission.transition(SubmissionStatus.TRANSMITTING)
    submission.transition(SubmissionStatus.SENT, adapter_id="internet", reference="provider-123")
    submission.transition(SubmissionStatus.RECEIVED, adapter_id="internet", reference="receipt-456")
    submission.transition(SubmissionStatus.ACKNOWLEDGED, adapter_id="internet", reference="ack-789")

    assert submission.status == SubmissionStatus.ACKNOWLEDGED
    assert [event.status for event in submission.events] == [
        SubmissionStatus.QUEUED,
        SubmissionStatus.TRANSMITTING,
        SubmissionStatus.SENT,
        SubmissionStatus.RECEIVED,
        SubmissionStatus.ACKNOWLEDGED,
    ]
