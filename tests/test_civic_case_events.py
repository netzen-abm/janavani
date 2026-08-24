import pytest

from src.core.civic_case import CaseEvent, CaseEventType
from src.storage.repositories.civic_case_events import InMemoryCivicCaseEventRepository


def test_audit_events_require_policy_and_preserve_case_scope():
    repo = InMemoryCivicCaseEventRepository()
    event = CaseEvent("event-1", "case-1", CaseEventType.SUBMITTED, "2026-08-24T00:00:00Z")

    with pytest.raises(PermissionError):
        repo.append(event, access_policy_ref="")

    repo.append(event, access_policy_ref="case-private")
    assert repo.list_for_case("case-1", access_policy_ref="case-private") == [event]
    assert repo.list_for_case("case-2", access_policy_ref="case-private") == []


def test_duplicate_audit_event_is_rejected():
    repo = InMemoryCivicCaseEventRepository()
    event = CaseEvent("event-1", "case-1", CaseEventType.SUBMITTED, "2026-08-24T00:00:00Z")
    repo.append(event, access_policy_ref="case-private")

    with pytest.raises(ValueError):
        repo.append(event, access_policy_ref="case-private")
