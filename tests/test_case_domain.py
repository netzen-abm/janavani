from datetime import timezone

from src.domain import Case, CaseStatus, CaseType


def test_case_is_channel_neutral_and_has_stable_id():
    case = Case(case_type=CaseType.COMPLAINT, subject="Streetlight failure")

    assert case.case_id
    assert case.status is CaseStatus.DRAFT
    assert case.created_at.tzinfo is timezone.utc
    assert case.updated_at.tzinfo is timezone.utc


def test_case_records_evidence_and_document_events():
    case = Case(subject="Road damage")

    evidence_event = case.add_evidence("evidence-1", actor_id="user-1")
    case.add_document("document-1", actor_id="user-1")

    assert case.evidence_refs == ["evidence-1"]
    assert case.document_refs == ["document-1"]
    assert evidence_event.case_id == case.case_id
    assert [event.event_type for event in case.events] == [
        "EVIDENCE_ADDED",
        "DOCUMENT_ADDED",
    ]


def test_case_status_transition_is_audited():
    case = Case(subject="Missing public service")

    event = case.transition(CaseStatus.READY, actor_id="user-1")

    assert case.status is CaseStatus.READY
    assert event.event_type == "READY"
    assert event.actor_id == "user-1"
    assert event.case_id == case.case_id
