from datetime import datetime, timezone

from src.domain.case import Case, CaseStatus
from src.domain.document import Document, DocumentType, PartyRef
from src.domain.evidence import Evidence, EvidenceKind
from src.storage.hydration import case_from_row, document_from_row, evidence_from_row
from src.storage.serialization import case_row, document_row, evidence_row


def test_case_row_round_trip_preserves_canonical_fields() -> None:
    case = Case(id="CASE-1", issue="Blocked drain", status=CaseStatus.REVIEW, facts={"ward": "12"})
    restored = case_from_row(case_row(case))
    assert restored.id == case.id
    assert restored.issue == case.issue
    assert restored.status == case.status
    assert restored.facts == case.facts


def test_evidence_row_round_trip_preserves_provenance_and_timestamp() -> None:
    captured_at = datetime(2026, 8, 28, 10, 30, tzinfo=timezone.utc)
    evidence = Evidence.create(
        "CASE-1",
        EvidenceKind.PHOTO,
        "Blocked drain",
        "citizen",
        content_ref="blob://evidence/1",
        captured_at=captured_at,
        metadata={"ward": "12"},
        provenance=["user-capture"],
    )
    restored = evidence_from_row(evidence_row(evidence))
    assert restored.evidence_id == evidence.evidence_id
    assert restored.case_id == evidence.case_id
    assert restored.kind == evidence.kind
    assert restored.provenance == evidence.provenance
    assert restored.captured_at == captured_at


def test_document_row_round_trip_preserves_parties_and_collections() -> None:
    document = Document.create(
        DocumentType.COMPLAINT,
        "Drain complaint",
        "en",
        PartyRef("office", "Municipal Engineering Office", email="office@example.org"),
        "Blocked drain",
        "Please investigate.",
        case_id="CASE-1",
        from_party=PartyRef("citizen", "Citizen", phone="+91-0000000000"),
        cc_parties=[PartyRef("office", "Ward Office")],
        references=["CASE-1"],
        enclosures=["EVD-1"],
    )
    restored = document_from_row(document_row(document))
    assert restored == document
