import pytest

from src.core.civic_case import CaseType, CivicCase
from src.core.civic_case_service import CivicCaseService
from src.storage.repositories.civic_case_events import InMemoryCivicCaseEventRepository
from src.storage.repositories.civic_case_repository import InMemoryCivicCaseRepository


def test_service_persists_state_and_matching_audit_event():
    cases = InMemoryCivicCaseRepository()
    events = InMemoryCivicCaseEventRepository()
    case = CivicCase("case-1", CaseType.COMPLAINT, "Road", "Broken road")
    cases.create(case, access_policy_ref="case-private")
    case.consent_refs.append("consent-1")

    service = CivicCaseService(cases, events)
    ready = service.mark_ready(case, access_policy_ref="case-private", occurred_at="2026-08-24T00:00:00Z")
    submitted = service.submit(case, access_policy_ref="case-private", occurred_at="2026-08-24T00:01:00Z", source_channel="api")

    assert ready.case_id == case.case_id
    assert submitted.event_type.value == "submitted"
    assert [e.event_id for e in events.list_for_case("case-1", access_policy_ref="case-private")] == [
        "ready:case-1",
        "submitted:case-1",
    ]


def test_service_does_not_create_audit_event_when_domain_transition_fails():
    cases = InMemoryCivicCaseRepository()
    events = InMemoryCivicCaseEventRepository()
    case = CivicCase("case-2", CaseType.COMPLAINT, "Road", "Broken road")
    cases.create(case, access_policy_ref="case-private")
    service = CivicCaseService(cases, events)

    with pytest.raises(PermissionError):
        service.mark_ready(case, access_policy_ref="case-private", occurred_at="2026-08-24T00:00:00Z")

    assert events.list_for_case("case-2", access_policy_ref="case-private") == []
