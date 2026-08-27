from dataclasses import dataclass

from src.domain.case import Case
from src.domain.submission import Submission
from src.storage.supabase_repositories import (
    SupabaseCaseRepository,
    SupabaseConfigurationError,
    SupabaseSubmissionRepository,
)


@dataclass
class _Response:
    data: list[dict]


class _Query:
    def __init__(self, table: str, rows: list[dict]) -> None:
        self.table = table
        self.rows = rows
        self.filters: list[tuple[str, object]] = []
        self.selected: str | None = None
        self.limit_value: int | None = None
        self.upsert_payload: dict | None = None

    def select(self, columns: str):
        self.selected = columns
        return self

    def eq(self, column: str, value: object):
        self.filters.append((column, value))
        return self

    def limit(self, value: int):
        self.limit_value = value
        return self

    def upsert(self, payload: dict):
        self.upsert_payload = payload
        return self

    def execute(self):
        if self.upsert_payload is not None:
            self.rows = [self.upsert_payload]
        return _Response(self.rows)


class _Client:
    def __init__(self, rows: list[dict] | None = None) -> None:
        self.rows = rows or []
        self.queries: list[_Query] = []

    def table(self, table: str) -> _Query:
        query = _Query(table, list(self.rows))
        self.queries.append(query)
        return query


def test_repository_requires_client() -> None:
    try:
        SupabaseCaseRepository(None)
    except SupabaseConfigurationError:
        pass
    else:
        raise AssertionError("expected missing client to be rejected")


def test_case_get_uses_canonical_table_and_id_filter() -> None:
    case = Case(issue="Pothole")
    client = _Client([{"id": case.id, "issue": case.issue, "status": case.status.value, "facts": {}}])
    hydrated = SupabaseCaseRepository(client).get(case.id)

    assert hydrated is not None
    assert hydrated.id == case.id
    query = client.queries[0]
    assert query.table == "cases"
    assert query.selected == "*"
    assert query.filters == [("id", case.id)]
    assert query.limit_value == 1


def test_case_get_returns_none_for_missing_record() -> None:
    assert SupabaseCaseRepository(_Client()).get("missing") is None


def test_case_save_upserts_serialized_row() -> None:
    case = Case(issue="Pothole")
    client = _Client()
    saved = SupabaseCaseRepository(client).save(case)

    assert saved.id == case.id
    query = client.queries[0]
    assert query.table == "cases"
    assert query.upsert_payload is not None
    assert query.upsert_payload["id"] == case.id
    assert query.upsert_payload["issue"] == case.issue


def test_submission_get_and_save_use_submission_id() -> None:
    submission = Submission(case_id="CASE-1", destination_ref="AUTH-1")
    row = {
        "submission_id": submission.submission_id,
        "operation_id": submission.operation_id,
        "case_id": submission.case_id,
        "destination_ref": submission.destination_ref,
        "status": submission.status.value,
    }
    client = _Client([row])
    repository = SupabaseSubmissionRepository(client)

    hydrated = repository.get(submission.submission_id)
    assert hydrated is not None
    assert hydrated.operation_id == submission.operation_id
    assert client.queries[0].table == "submissions"
    assert client.queries[0].filters == [("submission_id", submission.submission_id)]

    client = _Client()
    saved = SupabaseSubmissionRepository(client).save(submission)
    assert saved.submission_id == submission.submission_id
    assert client.queries[0].table == "submissions"
    assert client.queries[0].upsert_payload["operation_id"] == submission.operation_id
