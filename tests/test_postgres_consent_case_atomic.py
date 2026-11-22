from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import hashlib
import os
from typing import Any
from uuid import uuid4

import pytest

from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase
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
        if "SELECT created_by, version FROM civic_cases" in sql_text:
            self._row = ("citizen-1", 1)
        elif "RETURNING consent_id" in sql_text:
            self._row = ("consent-1",)
        else:
            self._row = None

    def fetchone(self):
        return getattr(self, "_row", None)

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


def consent():
    return Consent(
        consent_id="consent-1",
        subject_id="citizen-1",
        purpose="case_submission",
        scope=("submission",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-20T00:00:00+00:00",
    )



def add_consent_event(case: CivicCase, grant: Consent) -> CivicCase:
    case.events.append(CaseEvent(
        event_id=f"consent-{grant.consent_id}",
        case_id=case.case_id,
        event_type=CaseEventType.CONSENT_RECORDED,
        occurred_at=grant.created_at,
        actor_id=grant.subject_id,
        source_ref=grant.proof_ref,
        notes=grant.purpose,
    ))
    return case

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
    grant = consent()
    add_consent_event(case, grant)
    repo = PostgresConsentCaseAtomicRepository(
        connection_factory=lambda: conn,
        principal_id="citizen-1",
    )
    repo.save_consent_and_case(grant, case, principal_id="citizen-1")
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
    grant = consent()
    add_consent_event(case, grant)
    repo = PostgresConsentCaseAtomicRepository(connection_factory=lambda: conn)
    try:
        repo.save_consent_and_case(grant, case, principal_id="citizen-1")
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


def test_atomic_consent_keeps_draft_lifecycle_and_syncs_event_projection():
    conn = FakeConnection()
    case = CivicCase(
        case_id="case-atomic-draft",
        case_type=CaseType.COMPLAINT,
        subject="Road",
        narrative="Repair",
        created_by="citizen-1",
        status=CaseStatus.DRAFT,
        version=1,
        consent_refs=["consent-1"],
    )
    grant = consent()
    add_consent_event(case, grant)
    repo = PostgresConsentCaseAtomicRepository(connection_factory=lambda: conn)
    repo.save_consent_and_case(grant, case, principal_id="citizen-1")

    assert case.status is CaseStatus.DRAFT
    assert case.version == 2
    assert len(case.events) == 1
    assert case.events[0].event_type.value == "consent_recorded"


@pytest.mark.skipif(
    not os.getenv("JANAVANI_POSTGRES_TEST_DSN"),
    reason="requires the isolated PostgreSQL test DSN",
)
def test_postgres_consent_action_is_concurrent_idempotent_and_conflict_safe():
    import psycopg

    from src.storage.repositories.consent_case_atomic import ConsentIdempotencyConflictError

    schema = "consent_action_" + uuid4().hex
    dsn = os.environ["JANAVANI_POSTGRES_TEST_DSN"]

    with psycopg.connect(dsn, autocommit=True) as admin:
        admin.execute(f'CREATE SCHEMA "{schema}"')
        admin.execute(f'''
            CREATE TABLE "{schema}".civic_cases (
                case_id text PRIMARY KEY,
                created_by text NOT NULL,
                status text NOT NULL,
                updated_at timestamptz,
                version integer NOT NULL
            )
        ''')
        admin.execute(f'''
            CREATE TABLE "{schema}".civic_case_consents (
                consent_id text PRIMARY KEY,
                case_id text,
                purpose text NOT NULL,
                scope jsonb NOT NULL,
                grant_type text NOT NULL,
                status text NOT NULL,
                granted_by text NOT NULL,
                subject_id text NOT NULL,
                created_at timestamptz NOT NULL,
                expires_at timestamptz,
                revoked_at timestamptz,
                proof_ref text,
                action_fingerprint text
            )
        ''')
        admin.execute(f'''
            CREATE UNIQUE INDEX consent_subject_action_uidx
                ON "{schema}".civic_case_consents(subject_id, action_fingerprint)
                WHERE action_fingerprint IS NOT NULL
        ''')
        admin.execute(f'''
            CREATE TABLE "{schema}".civic_case_events (
                event_id text PRIMARY KEY,
                case_id text NOT NULL,
                event_type text NOT NULL,
                occurred_at timestamptz NOT NULL,
                actor_id text NOT NULL,
                source_channel text,
                source_ref text,
                notes text,
                event_version integer NOT NULL,
                created_at timestamptz NOT NULL
            )
        ''')
        admin.execute(
            f'INSERT INTO "{schema}".civic_cases '
            "(case_id, created_by, status, version) VALUES ('case-concurrent', 'citizen-1', 'draft', 1)"
        )

    def connect():
        connection = psycopg.connect(dsn)
        connection.execute(f'SET search_path TO "{schema}"')
        connection.commit()
        return connection

    repository = PostgresConsentCaseAtomicRepository(connection_factory=connect)
    first_consent = Consent(
        consent_id="consent-concurrent-1",
        subject_id="citizen-1",
        purpose="document_preparation",
        scope=("citizen_download_and_self_send",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-11-22T00:00:00+00:00",
        proof_ref="proof:action-1",
    )
    fingerprint = hashlib.sha256(b"telegram-update:concurrent-1").hexdigest()

    def perform_first_action(_):
        current_case = CivicCase(
            case_id="case-concurrent",
            case_type=CaseType.COMPLAINT,
            subject="Road",
            narrative="Repair",
            created_by="citizen-1",
            status=CaseStatus.DRAFT,
            version=1,
            consent_refs=[first_consent.consent_id],
        )
        add_consent_event(current_case, first_consent)
        return repository.save_consent_and_case(
            first_consent, current_case,
            principal_id="citizen-1", action_fingerprint=fingerprint,
        )

    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(perform_first_action, range(24)))
        assert {result.consent_id for result in results} == {"consent-concurrent-1"}

        second_consent = Consent(
            consent_id="consent-concurrent-2",
            subject_id="citizen-1",
            purpose="document_preparation",
            scope=("citizen_download_and_self_send",),
            grant_type=ConsentGrantType.EXPLICIT,
            status=ConsentStatus.GRANTED,
            created_at="2026-11-22T00:01:00+00:00",
            proof_ref="proof:action-2",
        )
        second_case = CivicCase(
            case_id="case-concurrent",
            case_type=CaseType.COMPLAINT,
            subject="Road",
            narrative="Repair",
            created_by="citizen-1",
            status=CaseStatus.DRAFT,
            version=2,
            consent_refs=["consent-concurrent-1", "consent-concurrent-2"],
        )
        add_consent_event(second_case, second_consent)
        repository.save_consent_and_case(
            second_consent, second_case,
            principal_id="citizen-1",
            action_fingerprint=hashlib.sha256(b"telegram-update:concurrent-2").hexdigest(),
        )

        conflicting = Consent(
            consent_id="consent-concurrent-conflict",
            subject_id="citizen-1",
            purpose="case_submission",
            scope=("office:other",),
            grant_type=ConsentGrantType.EXPLICIT,
            status=ConsentStatus.GRANTED,
            created_at="2026-11-22T00:02:00+00:00",
            proof_ref="proof:changed-payload",
        )
        with pytest.raises(ConsentIdempotencyConflictError):
            repository.save_consent_and_case(
                conflicting,
                CivicCase(
                    case_id="case-concurrent",
                    case_type=CaseType.COMPLAINT,
                    subject="Road",
                    narrative="Repair",
                    created_by="citizen-1",
                    status=CaseStatus.DRAFT,
                    version=3,
                    consent_refs=["consent-concurrent-1", "consent-concurrent-2",
                                  "consent-concurrent-conflict"],
                    events=[CaseEvent(
                        event_id="consent-consent-concurrent-conflict",
                        case_id="case-concurrent",
                        event_type=CaseEventType.CONSENT_RECORDED,
                        occurred_at=conflicting.created_at,
                        actor_id="citizen-1",
                        source_ref=conflicting.proof_ref,
                        notes=conflicting.purpose,
                    )],
                ),
                principal_id="citizen-1",
                action_fingerprint=fingerprint,
            )

        with psycopg.connect(dsn) as check:
            check.execute(f'SET search_path TO "{schema}"')
            consent_count = check.execute(
                "SELECT count(*) FROM civic_case_consents"
            ).fetchone()[0]
            event_count = check.execute(
                "SELECT count(*) FROM civic_case_events"
            ).fetchone()[0]
            version = check.execute(
                "SELECT version FROM civic_cases WHERE case_id='case-concurrent'"
            ).fetchone()[0]
            assert consent_count == 2
            assert event_count == 2
            assert version == 3
    finally:
        with psycopg.connect(dsn, autocommit=True) as admin:
            admin.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
