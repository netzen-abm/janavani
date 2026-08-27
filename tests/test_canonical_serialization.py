from datetime import datetime, timezone

from src.domain.authority import Authority, AuthoritySource
from src.domain.case import Case
from src.domain.consent import Consent
from src.domain.document import Document, DocumentType, PartyRef
from src.domain.evidence import Evidence, EvidenceKind
from src.domain.submission import Submission
from src.storage.serialization import (
    authority_row,
    case_row,
    consent_row,
    document_row,
    evidence_row,
    submission_row,
)


def test_case_row_is_stable() -> None:
    case = Case(issue="Road repair")
    row = case_row(case)
    assert row["id"] == case.id
    assert row["issue"] == "Road repair"
    assert row["status"] == case.status.value
    assert row["facts"] == case.facts


def test_evidence_row_preserves_metadata_and_provenance() -> None:
    evidence = Evidence.create(
        "CASE-1", EvidenceKind.DOCUMENT, "Order", "citizen",
        content_ref="blob://1", provenance=["official-ref"],
    )
    row = evidence_row(evidence)
    assert row["evidence_id"] == evidence.evidence_id
    assert row["kind"] == evidence.kind.value
    assert row["provenance"] == ["official-ref"]


def test_authority_row_serializes_sources() -> None:
    source = AuthoritySource(
        source_id="SRC-1", source_type="official_web",
        uri="https://example.gov", publisher="Example Government",
    )
    authority = Authority.create("Example Office", "office", source_refs=[source])
    row = authority_row(authority)
    assert row["authority_id"] == authority.authority_id
    assert row["source_refs"][0]["source_id"] == "SRC-1"


def test_consent_row_serializes_time_bounds() -> None:
    granted = datetime.now(timezone.utc)
    consent = Consent(
        consent_id="CON-1", subject_id="CASE-1", capability_id="CAP-SUBMIT",
        purpose="Submit representation", scope=("case",), data_categories=("personal",),
        status="granted", policy_version="v1", source_channel="web", granted_at=granted,
    )
    row = consent_row(consent)
    assert row["consent_id"] == "CON-1"
    assert row["scope"] == ["case"]
    assert row["granted_at"] == granted.isoformat()


def test_document_row_matches_canonical_document_fields() -> None:
    document = Document.create(
        DocumentType.COMPLAINT, "Complaint", "en", PartyRef("office", "Example Office"),
        "Delayed service", "Please investigate.", case_id="CASE-1",
    )
    row = document_row(document)
    assert row["document_id"] == document.document_id
    assert row["case_id"] == "CASE-1"
    assert row["document_type"] == "complaint"
    assert row["status"] == "draft"


def test_submission_row_preserves_idempotency_and_references() -> None:
    submission = Submission(
        case_id="CASE-1", destination_ref="AUTH-1",
        consent_ref="CON-1", authorization_ref="AUTHZ-1", payload_hash="sha256:x",
    )
    row = submission_row(submission)
    assert row["submission_id"] == submission.submission_id
    assert row["operation_id"] == submission.operation_id
    assert row["consent_ref"] == "CON-1"
    assert row["payload_hash"] == "sha256:x"
