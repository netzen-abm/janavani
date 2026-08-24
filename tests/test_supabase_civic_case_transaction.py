from types import SimpleNamespace

import pytest

from src.core.civic_case import CaseEvent, CaseEventType
from src.storage.repositories.supabase_civic_case_transaction import SupabaseCivicCaseTransaction


class FakeRpc:
    def __init__(self, calls):
        self.calls = calls

    def execute(self):
        return SimpleNamespace(data=[])


class FakeClient:
    def __init__(self):
        self.calls = []

    def rpc(self, name, payload):
        self.calls.append((name, payload))
        return FakeRpc(self.calls)


def test_atomic_transition_requires_policy():
    with pytest.raises(PermissionError):
        SupabaseCivicCaseTransaction(FakeClient()).commit_transition(
            "case-1",
            access_policy_ref="",
            status="submitted",
            event=CaseEvent("event-1", "case-1", CaseEventType.SUBMITTED, "2026-08-24T00:00:00Z"),
        )


def test_atomic_transition_uses_single_rpc_boundary():
    client = FakeClient()
    event = CaseEvent("event-2", "case-2", CaseEventType.SUBMITTED, "2026-08-24T00:00:00Z", source_channel="api")
    returned = SupabaseCivicCaseTransaction(client).commit_transition(
        "case-2", access_policy_ref="case-private", status="submitted", event=event
    )

    assert returned is event
    assert len(client.calls) == 1
    name, payload = client.calls[0]
    assert name == "append_civic_case_event"
    assert payload["p_case_id"] == "case-2"
    assert payload["p_status"] == "submitted"
    assert payload["p_event_id"] == "event-2"
