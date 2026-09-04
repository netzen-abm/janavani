from __future__ import annotations

import copy

import pytest

from src.core.civic_case import CaseEvent, CaseEventType, CaseType, CivicCase
from src.storage.repositories.supabase_civic_case import (
    CivicCaseConcurrencyError,
    SupabaseCivicCaseRepository,
)


class Response:
    def __init__(self, data):
        self.data = copy.deepcopy(data)


class Query:
    def __init__(self, client, table, operation="select", payload=None):
        self.client = client
        self.table = table
        self.operation = operation
        self.payload = payload
        self.filters = {}

    def select(self, _columns):
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
                    (row for row in rows if all(row.get(k) == item.get(k) for k in keys)),
                    None,
                )
                if match is None:
                    rows.append(copy.deepcopy(item))
                    changed.append(item)
                else:
                    match.update(copy.deepcopy(item))
                    changed.append(match)
            return Response(changed)
        raise AssertionError(self.operation)


class FakeSupabase:
    def __init__(self):
        self.tables = {
            "civic_case_consents": [{
                "case_id": "case-1",
                "consent_id": "consent-1",
            }],
        }

    def table(self, name):
        return Query(self, name)


def make_case() -> CivicCase:
    case = CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Broken road",
        narrative="The road is damaged.",
        created_by="citizen-1",
        jurisdiction={"district": "Pune"},
        related_office_id="office-1",
        claims=[{"claim": "road damage", "verified": False}],
        evidence_refs=["evidence-1"],
        document_refs=["document-1"],
        consent_refs=["consent-1"],
    )
    case.events.append(CaseEvent(
        event_id="event-1",
        case_id="case-1",
        event_type=CaseEventType.CREATED,
        occurred_at="2026-09-03T00:00:00+00:00",
        actor_id="citizen-1",
        source_channel="test",
        source_ref="ref-1",
        notes="created",
    ))
    return case


def test_supabase_repository_round_trip_preserves_case_contract():
    repository = SupabaseCivicCaseRepository(FakeSupabase())
    original = make_case()

    repository.save(original)
    loaded = repository.get(original.case_id)

    assert loaded is not None
    assert loaded.case_id == original.case_id
    assert loaded.case_type is original.case_type
    assert loaded.subject == original.subject
    assert loaded.narrative == original.narrative
    assert loaded.created_by == original.created_by
    assert loaded.jurisdiction == original.jurisdiction
    assert loaded.related_office_id == original.related_office_id
    assert loaded.claims == original.claims
    assert loaded.evidence_refs == original.evidence_refs
    assert loaded.document_refs == original.document_refs
    assert loaded.consent_refs == original.consent_refs
    assert loaded.status is original.status
    assert loaded.events == original.events
    assert loaded.version == 1
    assert loaded.created_at is not None
    assert loaded.updated_at is not None


def test_supabase_repository_advances_version_on_update():
    client = FakeSupabase()
    repository = SupabaseCivicCaseRepository(client)
    case = make_case()

    repository.save(case)
    case.subject = "Updated road"
    repository.save(case)

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
    with pytest.raises(CivicCaseConcurrencyError):
        second.save(stale)


def test_supabase_repository_is_not_constructible_without_client():
    with pytest.raises(ValueError):
        SupabaseCivicCaseRepository(None)
