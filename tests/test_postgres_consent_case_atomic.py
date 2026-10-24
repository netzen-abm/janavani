from dataclasses import dataclass
from copy import deepcopy
import os
from pathlib import Path
from uuid import uuid4
from typing import Any

import pytest

from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.civic_case import CaseStatus, CaseType, CivicCase
from src.storage.repositories.postgres_consent_case_atomic import PostgresConsentCaseAtomicRepository


@dataclass
class FakeCursor:
    fail_at: str | None = None
    calls: list[str] = None

    def __post_init__(self):
        self.calls = [] if self.calls is None else self.calls

    def execute(self, sql, params=None):
        sql_text = str(sql)
        self.calls.append(sql_text)
        self.rowcount = 1
        if self.fail_at and self.fail_at in sql_text:
            raise RuntimeError(f"forced failure: {self.fail_at}")
        if "SELECT version, status, created_by, updated_at FROM civic_cases" in sql_text:
            self._row = (1, "draft", "citizen-1", "2026-09-20T00:00:00+00:00")
        else:
            self._row = None

    def fetchone(self):
        return getattr(self, "_row", None)

    def fetchall(self):
        return []

    def executemany(self, sql, params):
        self.calls.append(str(sql))
        self.rowcount = len(list(params))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeTransaction:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.events.append("BEGIN")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.events.append("ROLLBACK" if exc_type else "COMMIT")
        return False


class FakeConnection:
    def __init__(self, fail_at=None):
        self.events = []
        self.fail_at = fail_at

    def transaction(self):
        return FakeTransaction(self)

    def cursor(self):
        return FakeCursor(self.fail_at)

    def close(self):
        self.events.append("CLOSE")

    def execute(self, sql, params=None):
        return None


def consent(consent_id="consent-1", subject_id="citizen-1"):
    return Consent(
        consent_id=consent_id,
        subject_id=subject_id,
        purpose="case_submission",
        scope=("submission",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-20T00:00:00+00:00",
    )


def test_atomic_consent_case_commits_all_writes():
    conn = FakeConnection()
    case = CivicCase(
        case_id="case-atomic-1",
        case_type=CaseType.COMPLAINT,
        subject="Road",
        narrative="Repair",
        created_by="citizen-1",
        status=CaseStatus.REVIEW,
        version=1,
        consent_refs=["consent-1"],
    )
    repo = PostgresConsentCaseAtomicRepository(
        connection_factory=lambda: conn,
        principal_id="citizen-1",
    )
    repo.save_consent_and_case(consent(), case, principal_id="citizen-1")
    assert "BEGIN" in conn.events
    assert "COMMIT" in conn.events
    assert "ROLLBACK" not in conn.events
    assert case.version == 2


def test_atomic_consent_case_rolls_back_when_case_update_fails():
    conn = FakeConnection(fail_at="UPDATE civic_cases")
    case = CivicCase(
        case_id="case-atomic-2",
        case_type=CaseType.COMPLAINT,
        subject="Road",
        narrative="Repair",
        created_by="citizen-1",
        status=CaseStatus.REVIEW,
        version=1,
        consent_refs=["consent-1"],
    )
    repo = PostgresConsentCaseAtomicRepository(connection_factory=lambda: conn)
    try:
        repo.save_consent_and_case(consent(), case, principal_id="citizen-1")
    except RuntimeError:
        pass
    else:
        raise AssertionError("forced Case failure must roll back")
    assert "ROLLBACK" in conn.events
    assert "COMMIT" not in conn.events


def test_atomic_consent_case_rejects_cross_user_consent():
    conn = FakeConnection()
    repo = PostgresConsentCaseAtomicRepository(connection_factory=lambda: conn)
    try:
        repo.save_consent_and_case(consent(), CivicCase(
            case_id="case-atomic-3",
            case_type=CaseType.COMPLAINT,
            subject="Road",
            narrative="Repair",
            created_by="citizen-1",
            status=CaseStatus.REVIEW,
            version=1,
            consent_refs=["consent-1"],
        ), principal_id="other-user")
    except PermissionError:
        pass
    else:
        raise AssertionError("cross-user consent must be rejected")
    assert "BEGIN" not in conn.events


def test_atomic_consent_case_requires_consent_reference():
    conn = FakeConnection()
    repo = PostgresConsentCaseAtomicRepository(connection_factory=lambda: conn)
    case = CivicCase(
        case_id="case-atomic-4",
        case_type=CaseType.COMPLAINT,
        subject="Road",
        narrative="Repair",
        created_by="citizen-1",
        status=CaseStatus.REVIEW,
        version=1,
    )
    try:
        repo.save_consent_and_case(consent(), case, principal_id="citizen-1")
    except ValueError:
        pass
    else:
        raise AssertionError("missing consent reference must be rejected")


def test_atomic_consent_case_rejects_case_owned_by_other_principal():
    conn = FakeConnection()
    repo = PostgresConsentCaseAtomicRepository(connection_factory=lambda: conn)
    case = CivicCase(
        case_id="case-atomic-5",
        case_type=CaseType.COMPLAINT,
        subject="Road",
        narrative="Repair",
        created_by="other-user",
        status=CaseStatus.REVIEW,
        version=1,
        consent_refs=["consent-1"],
    )
    try:
        repo.save_consent_and_case(consent(), case, principal_id="citizen-1")
    except PermissionError:
        pass
    else:
        raise AssertionError("cross-user Case must be rejected")



@pytest.mark.skipif(
    not os.getenv("JANAVANI_POSTGRES_TEST_DSN"),
    reason="requires JANAVANI_POSTGRES_TEST_DSN",
)
def test_postgres_atomic_consent_case_replay_is_idempotent_after_lost_response():
    import psycopg
    from psycopg import sql

    dsn = os.getenv("JANAVANI_POSTGRES_TEST_DSN", "").strip()
    runtime_dsns = {
        os.getenv(key, "").strip()
        for key in ("JANAVANI_POSTGRES_DSN", "JANAVANI_IDENTITY_LINKS_DSN", "JANAVANI_CASE_DATABASE_URL")
    } - {""}
    if dsn in runtime_dsns:
        pytest.fail("JANAVANI_POSTGRES_TEST_DSN must be separate from runtime DSNs")
    if os.getenv("JANAVANI_RUNTIME_MODE", "development").strip().lower() == "production":
        pytest.fail("Refusing atomic integration test in production mode")
    if not any(marker in dsn.lower() for marker in ("test", "localhost", "127.0.0.1")):
        pytest.fail("DSN must identify a test/local database")

    root = Path(__file__).resolve().parents[1]
    schema = (root / "db/migrations/20260912100000_canonical_case_policy_schema.sql").read_text()
    token = uuid4().hex
    principal = f"consent-replay-{token}"
    case_id, consent_id = f"case-{token}", f"consent-{token}"
    rollback_token = uuid4().hex
    rollback_principal = f"consent-rollback-{rollback_token}"
    rollback_case_id = f"case-{rollback_token}"
    rollback_consent_id = f"consent-{rollback_token}"
    rollback_constraint = f"ck_consent_rollback_{rollback_token}"
    timestamp = "2026-10-22T00:00:00+00:00"
    with psycopg.connect(dsn) as connection:
        connection.execute(schema)
        connection.execute(
            """INSERT INTO public.civic_cases
               (case_id, case_type, subject, narrative, created_by, status, created_at, updated_at, version)
               VALUES (%s, 'complaint', 'complaint', '', %s, 'draft', %s, %s, 1)""",
            (case_id, principal, timestamp, timestamp),
        )
        connection.execute(
            """INSERT INTO public.civic_cases
               (case_id, case_type, subject, narrative, created_by, status, created_at, updated_at, version)
               VALUES (%s, 'complaint', 'complaint', '', %s, 'draft', %s, %s, 1)""",
            (rollback_case_id, rollback_principal, timestamp, timestamp),
        )
        # A NOT VALID constraint is enforced on changed rows but does not scan
        # unrelated pre-existing data. It forces the Case UPDATE to fail after
        # the atomic repository has attempted the consent INSERT.
        connection.execute(
            sql.SQL(
                "ALTER TABLE public.civic_cases ADD CONSTRAINT {} "
                "CHECK (case_id <> {} OR status <> 'ready') NOT VALID"
            ).format(
                sql.Identifier(rollback_constraint),
                sql.Literal(rollback_case_id),
            )
        )

    case = CivicCase(
        case_id=case_id, case_type=CaseType.COMPLAINT, subject="Road repairs",
        narrative="Private narrative held outside the durable Case row",
        created_by=principal, status=CaseStatus.DRAFT, version=1,
        created_at=timestamp, updated_at=timestamp, consent_refs=[consent_id],
    )
    case.start_review(event_id=f"review-{token}", occurred_at=timestamp, actor_id=principal)
    case.mark_ready(event_id=f"approve-{token}", occurred_at=timestamp, actor_id=principal)
    stale_retry = deepcopy(case)
    repository = PostgresConsentCaseAtomicRepository(dsn=dsn, principal_id=principal)

    try:
        repository.save_consent_and_case(consent(consent_id, principal), case, principal_id=principal)
        assert case.version == 2
        # Simulate a worker losing its acknowledgement after the DB commit: retry the
        # original version-1 operation with the same idempotency identity and event IDs.
        repository.save_consent_and_case(consent(consent_id, principal), stale_retry, principal_id=principal)
        assert stale_retry.version == 2

        with psycopg.connect(dsn) as connection:
            persisted = connection.execute(
                "SELECT status, version FROM public.civic_cases WHERE case_id=%s", (case_id,)
            ).fetchone()
            consent_count = connection.execute(
                "SELECT count(*) FROM public.civic_case_consents WHERE consent_id=%s", (consent_id,)
            ).fetchone()[0]
            events = connection.execute(
                "SELECT event_type FROM public.civic_case_events WHERE case_id=%s ORDER BY event_type",
                (case_id,),
            ).fetchall()
        assert persisted == ("ready", 2)
        assert consent_count == 1
        assert [event[0] for event in events] == ["approved", "consent_recorded", "review_started"]

        rollback_case = CivicCase(
            case_id=rollback_case_id,
            case_type=CaseType.COMPLAINT,
            subject="Rollback transaction",
            narrative="Private content remains outside durable Case metadata",
            created_by=rollback_principal,
            status=CaseStatus.READY,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
            consent_refs=[rollback_consent_id],
        )
        rollback_repository = PostgresConsentCaseAtomicRepository(
            dsn=dsn,
            principal_id=rollback_principal,
        )
        with pytest.raises(psycopg.errors.CheckViolation):
            rollback_repository.save_consent_and_case(
                consent(rollback_consent_id, rollback_principal),
                rollback_case,
                principal_id=rollback_principal,
            )

        # The real PostgreSQL constraint fails after the consent INSERT was
        # attempted. The transaction must roll back consent, Case status/version,
        # and lifecycle events together.
        with psycopg.connect(dsn) as connection:
            persisted_case = connection.execute(
                "SELECT status, version FROM public.civic_cases WHERE case_id=%s",
                (rollback_case_id,),
            ).fetchone()
            persisted_consent_count = connection.execute(
                "SELECT count(*) FROM public.civic_case_consents WHERE consent_id=%s",
                (rollback_consent_id,),
            ).fetchone()[0]
            rollback_events = connection.execute(
                "SELECT count(*) FROM public.civic_case_events WHERE case_id=%s",
                (rollback_case_id,),
            ).fetchone()[0]
        assert persisted_case == ("draft", 1)
        assert persisted_consent_count == 0
        assert rollback_events == 0
    finally:
        with psycopg.connect(dsn) as connection:
            with connection.transaction():
                connection.execute(
                    sql.SQL("ALTER TABLE public.civic_cases DROP CONSTRAINT IF EXISTS {}")
                    .format(sql.Identifier(rollback_constraint))
                )
                for candidate_case_id in (case_id, rollback_case_id):
                    connection.execute(
                        "DELETE FROM public.civic_case_events WHERE case_id=%s",
                        (candidate_case_id,),
                    )
                for candidate_consent_id in (consent_id, rollback_consent_id):
                    connection.execute(
                        "DELETE FROM public.civic_case_consents WHERE consent_id=%s",
                        (candidate_consent_id,),
                    )
                for candidate_case_id in (case_id, rollback_case_id):
                    connection.execute(
                        "DELETE FROM public.civic_cases WHERE case_id=%s",
                        (candidate_case_id,),
                    )
