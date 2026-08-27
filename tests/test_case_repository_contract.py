from __future__ import annotations

from pathlib import Path

from src.domain import Case, CaseType
from src.storage.complaint_repository import ComplaintRepository


def _case_record(case: Case) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "case_type": case.case_type.value,
        "created_by": case.created_by,
        "subject": case.subject,
        "narrative": case.narrative,
        "status": case.status.value,
        "evidence_refs": list(case.evidence_refs),
        "document_refs": list(case.document_refs),
        "events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "source_ref": event.source_ref,
            }
            for event in case.events
        ],
    }


def test_jsonl_adapter_round_trips_canonical_case_id(tmp_path: Path) -> None:
    case = Case(
        case_type=CaseType.COMPLAINT,
        created_by="citizen-1",
        subject="Road repair",
        narrative="Road needs repair.",
    )
    case.add_evidence("evidence-1", actor_id="citizen-1")
    record = _case_record(case)

    repository = ComplaintRepository(tmp_path / "cases.jsonl")
    repository.save(record)

    loaded = repository.get_by_id(case.case_id)
    assert loaded is not None
    assert loaded["case_id"] == case.case_id
    assert loaded["subject"] == "Road repair"
    assert loaded["evidence_refs"] == ["evidence-1"]
    assert len(loaded["events"]) == 1


def test_jsonl_adapter_reads_legacy_complaint_id(tmp_path: Path) -> None:
    repository = ComplaintRepository(tmp_path / "complaints.jsonl")
    repository.save({"complaint_id": "legacy-1", "subject": "Legacy complaint"})

    loaded = repository.get_by_id("legacy-1")
    assert loaded is not None
    assert loaded["complaint_id"] == "legacy-1"
    assert loaded["case_id"] == "legacy-1"
