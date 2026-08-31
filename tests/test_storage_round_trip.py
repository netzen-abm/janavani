from datetime import datetime, timezone

from src.domain.authority import Authority, AuthoritySource
from src.domain.case import Case
from src.domain.consent import Consent, ConsentStatus
from src.domain.document import Document, DocumentType, PartyRef
from src.domain.evidence import Evidence, EvidenceKind
from src.domain.submission import Submission
from src.storage.hydration import (
    authority_from_row,
    case_from_row,
    consent_from_row,
    document_from_row,
    evidence_from_row,
    submission_from_row,
)
from src.storage.serialization import (
    authority_row,
    case_row,
    consent_row,
    document_row,
    evidence_row,
    submission_row,
)


def test_case_round_trip() -> None:
    case = Case(issue="Road repair")
    assert case_from_row(case_row(case)).id == case.id
    assert case_from_row(case_row(case)).issue == case.issue


def test_evidence_round_trip() -> None:
    evidence = Evidence.create(
        "CASE-1", EvidenceKind.DOCUMENT, "Order", "citizen",
        content_ref="blob://1", provenance=["official-ref"],
    )
    hydrated = evidence_from_row(evidence_row(evidence))
    assert hydrated.evidence_id == evidence.evidence_id
    assert hydrated.provenance == evidence.provenance


def test_authority_round_trip() -> None:
    source = AuthoritySource(
        source_id="SRC-1", source_type="official_web",
        uri="https://example.gov", publisher="Example Government",
    )
    authority = Authority.create("Example Office", "office", source_refs=[source])
    hydrated = authority_from_row(authority_row(authority))
    assert hydrated.authority_id == authority.authority_id
    assert hydrated.source_refs[0].source_id == "SRC-1"


def test_consent_round_trip() -> None:
    granted = datetime.now(timezone.utc)
    consent = Consent(
        consent_id="CON-1", subject_id="CASE-1", capability_id="CAP-SUBMIT",
        purpose="Submit representation", scope=("case",), data_categories=("personal",),
        status=ConsentStatus.GRANTED, policy_version="v1", source_channel="web", granted_at=granted,
    )
    hydrated = consent_from_row(consent_row(consent))
    assert hydrated.consent_id == consent.consent_id
    assert hydrated.granted_at == granted


def test_document_round_trip() -> None:
    document = Document.create(
        DocumentType.COMPLAINT, "Complaint", "en", PartyRef("office", "Example Office"),
        "Delayed service", "Please investigate.", case_id="CASE-1",
    )
    hydrated = document_from_row(document_row(document))
    assert hydrated.document_id == document.document_id
    assert hydrated.case_id == "CASE-1"
    assert hydrated.title == document.title


def test_submission_round_trip() -> None:
    submission = Submission(
        case_id="CASE-1", destination_ref="AUTH-1",
        consent_ref="CON-1", authorization_ref="AUTHZ-1", payload_hash="sha256:x",
    )
    hydrated = submission_from_row(submission_row(submission))
    assert hydrated.submission_id == submission.submission_id
    assert hydrated.operation_id == submission.operation_id
    assert hydrated.payload_hash == submission.payload_hash
