from __future__ import annotations

import copy

from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
from src.storage.repositories.supabase_civic_case import (
    CivicCaseConcurrencyError,
    SupabaseCivicCaseRepository,
)


class Response:
    def __init__(self, data):
        self.data = data


class Query:
    def __init__(self, client, table):
        self.client = client
        self.table = table
        self.operation = "select"
        self.filters = {}
        self.payload = None
        self.on_conflict = None

    def select(self, *_args):
        self.operation = "select"
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = payload
        return self

    def upsert(self, payload, on_conflict=None):
        self.operation = "upsert"
        self.payload = payload
        self.on_conflict = on_conflict
        return self

    def execute(self):
        rows = self.client.tables.setdefault(self.table, [])
        if self.operation == "select":
            return Response([
                row for row in rows
                if all(row.get(k) == v for k, v in self.filters.items())
            ])
        payload = self.payload
        if not isinstance(payload, list):
            payload = [payload]
        if self.operation == "insert":
            rows.extend(copy.deepcopy(payload))
            return Response(payload)
        if self.operation == "update":
            changed = []
            update_values = payload[0] if len(payload) == 1 else payload
            for row in rows:
                if all(row.get(k) == v for k, v in self.filters.items()):
                    row.update(copy.deepcopy(update_values))
                    changed.append(row)
            return Response(changed)
        if self.operation == "upsert":
            keys = ["case_id", "evidence_id", "relationship"]
            if self.table == "civic_case_document_refs":
                keys = ["case_id", "document_id", "relationship"]
            changed = []
            for item in payload:
                match = next(
                    (row for row in rows if all(row.get(key) == item.get(key) for key in keys)),
                    None,
                )
                if match is None:
                    rows.append(copy.deepcopy(item))
                    changed.append(item)
                else:
                    match.update(copy.deepcopy(item))
                    changed.append(match)
            return Response(changed)
        raise AssertionError(f"Unsupported operation: {self.operation}")


class FakeSupabase:
    def __init__(self):
        self.tables = {}

    def table(self, table):
        return Query(self, table)


def make_case():
    return CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Broken road",
        narrative="The road is damaged.",
        status=CaseStatus.DRAFT,
        events=[CaseEvent(
            event_id="event-1",
            case_id="case-1",
            event_type=CaseEventType.CREATED,
            occurred_at="2026-09-04T00:00:00+00:00",
        )],
    )


def test_supabase_repository_round_trip_preserves_case_contract():
    client = FakeSupabase()
    repository = SupabaseCivicCaseRepository(client)
    case = make_case()
    repository.save(case)
    loaded = repository.get(case.case_id)
    assert loaded is not None
    assert loaded.subject == case.subject
    assert loaded.version == 1
    assert loaded.events[0].event_id == "event-1"


def test_supabase_repository_advances_version_on_update():
    client = FakeSupabase()
    repository = SupabaseCivicCaseRepository(client)
    case = make_case()

    repository.save(case)
    case.subject = "Updated road"
    repository.save(case)

    assert case.version == 2
    loaded = repository.get(case.case_id)
    assert loaded is not None
    assert loaded.subject == "Updated road"
    assert loaded.version == 2


def test_supabase_repository_rejects_stale_version():
    client = FakeSupabase()
    first = SupabaseCivicCaseRepository(client)
    second = SupabaseCivicCaseRepository(client)
    case = make_case()

    first.save(case)
    stale = second.get(case.case_id)
    assert stale is not None

    case.subject = "Current update"
    first.save(case)

    stale.subject = "Stale update"
    try:
        second.save(stale)
    except CivicCaseConcurrencyError:
        pass
    else:
        raise AssertionError("Expected stale version to be rejected")


def test_supabase_repository_is_not_constructible_without_client():
    try:
        SupabaseCivicCaseRepository(None)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected missing client to be rejected")
