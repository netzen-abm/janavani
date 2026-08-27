from src.domain.case import Case, CaseStatus


def test_case_starts_open_and_records_transitions() -> None:
    case = Case(issue="Broken streetlight on Main Road")

    assert case.status is CaseStatus.OPEN
    assert case.issue == "Broken streetlight on Main Road"
    assert case.events == []

    case.transition(CaseStatus.EVIDENCE_COLLECTION, actor="citizen")

    assert case.status is CaseStatus.EVIDENCE_COLLECTION
    assert len(case.events) == 1
    assert case.events[0].event_type == "case.status_changed"
    assert case.events[0].data == {
        "from": "open",
        "to": "evidence_collection",
    }


def test_repeated_transition_is_idempotent() -> None:
    case = Case(issue="Road damage")
    case.transition(CaseStatus.REVIEW)
    case.transition(CaseStatus.REVIEW)

    assert len(case.events) == 1


def test_empty_issue_is_rejected() -> None:
    try:
        Case(issue="   ")
    except ValueError as exc:
        assert str(exc) == "case issue is required"
    else:
        raise AssertionError("empty case issue should be rejected")


def test_case_attaches_evidence_identity_and_records_event() -> None:
    case = Case(issue="Broken streetlight")
    case.attach_evidence("EVD-123", actor="citizen")

    assert case.evidence_ids == ["EVD-123"]
    assert case.events[-1].event_type == "case.evidence_attached"
    assert case.events[-1].data == {"evidence_id": "EVD-123"}


def test_duplicate_evidence_attachment_is_idempotent() -> None:
    case = Case(issue="Road damage")
    case.attach_evidence("EVD-123")
    case.attach_evidence("EVD-123")

    assert case.evidence_ids == ["EVD-123"]
    assert len(case.events) == 1


def test_blank_evidence_identity_is_rejected() -> None:
    case = Case(issue="Road damage")

    try:
        case.attach_evidence("   ")
    except ValueError as exc:
        assert str(exc) == "evidence_id is required"
    else:
        raise AssertionError("blank evidence identity should be rejected")
