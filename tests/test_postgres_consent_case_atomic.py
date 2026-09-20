from dataclasses import dataclass
from typing import Any

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
        if self.fail_at and self.fail_at in sql_text:
            raise RuntimeError(f"forced failure: {self.fail_at}")
        if "SELECT version FROM civic_cases" in sql_text:
            self._row = (1,)
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
