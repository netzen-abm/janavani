from core.civic_case import CaseStatus, CaseType
from services.case_migration import session_to_civic_case


def test_legacy_session_translates_to_canonical_case():
    case = session_to_civic_case({
        "complaint_id": "JV-001",
        "issue": "Streetlight is not working",
        "district": "Pune",
        "department": "Municipal Corporation",
        "office": {"id": "OFF-7"},
    })

    assert case.case_id == "JV-001"
    assert case.case_type is CaseType.COMPLAINT
    assert case.status is CaseStatus.DRAFT
    assert case.narrative == "Streetlight is not working"
    assert case.related_office_id == "OFF-7"
    assert case.events[0].event_type.value == "created"
    assert case.events[0].source_channel == "telegram"
