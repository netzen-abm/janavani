from types import SimpleNamespace

import pytest

from src.core.civic_case import CaseType, CivicCase
from src.storage.repositories.supabase_civic_case_repository import SupabaseCivicCaseRepository


class FakeQuery:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else []

    def insert(self, payload):
        self.rows.append(payload)
        return self

    def select(self, *_):
        return self

    def update(self, payload):
        self.rows[:] = [payload]
        return self

    def eq(self, *_):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


class FakeClient:
    def __init__(self):
        self.rows = []
        self.query = FakeQuery(self.rows)

    def table(self, _):
        return self.query


def test_supabase_adapter_requires_policy():
    repo = SupabaseCivicCaseRepository(FakeClient())
    case = CivicCase("case-1", CaseType.COMPLAINT, "Road", "Broken road")
    with pytest.raises(PermissionError):
        repo.create(case, access_policy_ref="")


def test_supabase_adapter_round_trips_case_metadata_only():
    client = FakeClient()
    repo = SupabaseCivicCaseRepository(client)
    case = CivicCase("case-2", CaseType.COMPLAINT, "Road", "Broken road", created_by="identity-ref")

    repo.create(case, access_policy_ref="case-private")
    assert client.rows[0]["access_policy_ref"] == "case-private"
    assert client.rows[0]["created_by_ref"] == "identity-ref"
    assert "evidence_bytes" not in client.rows[0]

    loaded = repo.get("case-2", access_policy_ref="case-private")
    assert loaded is not None
    assert loaded.case_id == case.case_id
    assert loaded.subject == case.subject
