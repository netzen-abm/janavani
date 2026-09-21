from core.civic_case import CaseStatus, CaseType
from services.case_migration import session_to_civic_case


def test_legacy_session_translates_to_owned_canonical_case():
    case = session_to_civic_case({
        "complaint_id": "JV-001",
        "telegram_user_id": 12345,
        "issue": "Streetlight is not working",
        "district": "Pune",
        "department": "Municipal Corporation",
        "office": {"id": "OFF-7"},
    })

    assert case.case_id == "JV-001"
    assert case.case_type is CaseType.COMPLAINT
    assert case.status is CaseStatus.DRAFT
    assert case.narrative == "Streetlight is not working"
    assert case.created_by == "telegram:12345"
    assert case.related_office_id == "OFF-7"
    assert case.events[0].event_type.value == "created"
    assert case.events[0].source_channel == "telegram"
    assert case.events[0].actor_id == "telegram:12345"


def test_legacy_session_requires_telegram_identity():
    try:
        session_to_civic_case({"complaint_id": "JV-002", "issue": "Road damaged"})
    except ValueError as exc:
        assert "telegram_user_id" in str(exc)
    else:
        raise AssertionError("case migration must require a Telegram principal")
