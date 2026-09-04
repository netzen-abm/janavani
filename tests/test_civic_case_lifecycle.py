from src.core.civic_case import CaseEventType, CaseStatus, CivicCase, validate_event_chain


def _case(status=CaseStatus.DRAFT, *, consent=True):
    return CivicCase(
        case_id="case-1",
        case_type="complaint",
        subject="Road damage",
        narrative="Road is damaged",
        status=status,
        consent_refs=["consent-1"] if consent else [],
    )


def test_transition_matrix_happy_path():
    case = _case()
    case.start_review(event_id="e1", occurred_at="2026-01-01T00:00:00Z")
    case.mark_ready(event_id="e2", occurred_at="2026-01-01T00:01:00Z")
    case.begin_submission(event_id="e3", occurred_at="2026-01-01T00:02:00Z")
    case.queue_submission(event_id="e4", occurred_at="2026-01-01T00:03:00Z")
    case.submit(event_id="e5", occurred_at="2026-01-01T00:04:00Z")
    case.acknowledge(event_id="e6", occurred_at="2026-01-01T00:05:00Z")
    case.follow_up(event_id="e7", occurred_at="2026-01-01T00:06:00Z")
    case.respond(event_id="e8", occurred_at="2026-01-01T00:07:00Z")
    case.resolve(event_id="e9", occurred_at="2026-01-01T00:08:00Z")
    case.close(event_id="e10", occurred_at="2026-01-01T00:09:00Z")
    assert case.status is CaseStatus.CLOSED
    assert validate_event_chain(case.events)


def test_ready_requires_explicit_consent():
    case = _case(consent=False)
    case.start_review(event_id="e1", occurred_at="2026-01-01T00:00:00Z")
    try:
        case.mark_ready(event_id="e2", occurred_at="2026-01-01T00:01:00Z")
    except PermissionError:
        pass
    else:
        raise AssertionError("READY must require explicit consent")


def test_invalid_transitions_fail_closed():
    case = _case()
    for method, kwargs in [
        (case.begin_submission, dict(event_id="e1", occurred_at="now")),
        (case.submit, dict(event_id="e2", occurred_at="now")),
        (case.acknowledge, dict(event_id="e3", occurred_at="now")),
        (case.resolve, dict(event_id="e4", occurred_at="now")),
        (case.close, dict(event_id="e5", occurred_at="now")),
    ]:
        try:
            method(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid transition was accepted")


def test_event_chain_rejects_events_after_closed():
    case = _case(status=CaseStatus.CLOSED)
    case.events = [
        case._record.__self__.events[0]
    ] if False else []
    # validate_event_chain's closed-state guard is represented by the event sequence;
    # construct a minimal valid prefix followed by a post-close event.
    from src.core.civic_case import CaseEvent
    events = [
        CaseEvent("e1", "case-1", CaseEventType.CREATED, "now"),
        CaseEvent("e2", "case-1", CaseEventType.CLOSED, "now"),
        CaseEvent("e3", "case-1", CaseEventType.EDITED, "now"),
    ]
    assert not validate_event_chain(events)
