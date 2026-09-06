import json
import os
from pathlib import Path

import pytest

from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
from src.storage.repositories.postgres_civic_case import (
    PostgresCivicCasePersistenceError,
    PostgresCivicCaseRepository,
)


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def repository():
    dsn = os.getenv("JANAVANI_POSTGRES_DSN")
    if not dsn:
        pytest.skip("JANAVANI_POSTGRES_DSN is not configured")
    import psycopg

    schema = Path("docs/architecture/POSTGRESQL_MIGRATION_DRAFT.sql").read_text(
        encoding="utf-8"
    )
    with psycopg.connect(dsn) as conn:
        conn.execute(schema)
    return PostgresCivicCaseRepository(dsn=dsn)


def _case() -> CivicCase:
    return CivicCase(
        case_id="integration-postgres-case",
        case_type=CaseType.COMPLAINT,
        subject="Heterogeneous PostgreSQL round trip",
        narrative="Verify canonical CivicCase persistence against a real database.",
        created_by="integration-test",
        jurisdiction={
            "district": "Test District",
            "priority": 3,
            "score": 4.5,
            "tags": ["civic", "integration"],
            "nested": {"enabled": True},
        },
        related_organisation_id="org-test",
        related_office_id="office-test",
        related_official_id="official-test",
        related_representative_id="representative-test",
        claims=[
            {"kind": "fact", "verified": False, "amount": 1250},
            {"kind": "context", "items": ["a", 2, True]},
        ],
        evidence_refs=["evidence-test"],
        document_refs=["document-test"],
        status=CaseStatus.REVIEW,
        events=[
            CaseEvent(
                event_id="integration-event-1",
                case_id="integration-postgres-case",
                event_type=CaseEventType.CREATED,
                occurred_at="2026-09-06T00:00:00+00:00",
                actor_id="integration-test",
                source_channel="test",
                source_ref="fixture",
                notes="Initial integration event",
            )
        ],
    )


def test_real_postgres_round_trip_preserves_canonical_fields(repository):
    case = _case()
    repository.save(case)
    loaded = repository.get(case.case_id)

    assert loaded is not None
    assert loaded.case_type == case.case_type
    assert loaded.subject == case.subject
    assert loaded.narrative == case.narrative
    assert loaded.created_by == case.created_by
    assert loaded.jurisdiction == case.jurisdiction
    assert loaded.claims == case.claims
    assert loaded.evidence_refs == case.evidence_refs
    assert loaded.document_refs == case.document_refs
    assert loaded.status == case.status
    assert loaded.version == case.version
    assert loaded.events == case.events


def test_real_postgres_json_fixture_matches_canonical_shape(repository):
    fixture = json.loads(
        Path("tests/fixtures/civic_case_serialization.json").read_text(
            encoding="utf-8"
        )
    )
    case = _case()
    case.case_id = "integration-postgres-fixture-case"
    case.events[0].case_id = case.case_id
    case.jurisdiction = fixture["jurisdiction"]
    case.claims = fixture["claims"]
    repository.save(case)
    loaded = repository.get(case.case_id)

    assert loaded is not None
    assert loaded.jurisdiction == fixture["jurisdiction"]
    assert loaded.claims == fixture["claims"]


def test_real_postgres_stale_version_is_rejected(repository):
    case = _case()
    case.case_id = "integration-postgres-concurrency-case"
    case.events[0].case_id = case.case_id
    repository.save(case)
    stale = repository.get(case.case_id)
    assert stale is not None
    current = repository.get(case.case_id)
    assert current is not None

    current.subject = "Newer committed subject"
    repository.save(current)

    with pytest.raises(PostgresCivicCasePersistenceError):
        repository.save(stale)


def test_real_postgres_transaction_rolls_back_on_provider_failure(repository):
    case = _case()
    case.case_id = "integration-postgres-rollback-case"
    case.events[0].case_id = case.case_id

    original = repository._persist_refs

    def fail_after_case_and_event(cur, candidate):
        original(cur, candidate)
        raise RuntimeError("forced integration rollback")

    repository._persist_refs = fail_after_case_and_event
    try:
        with pytest.raises(PostgresCivicCasePersistenceError):
            repository.save(case)
    finally:
        repository._persist_refs = original

    assert repository.get(case.case_id) is None
