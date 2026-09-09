from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.storage.repositories.postgres_consent import PostgresConsentRepository


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=()):
        upper = sql.upper()
        if "SELECT CONSENT_ID" in upper:
            item = self.db.items.get(params[0])
            self.rows = [item] if item else []
        elif "WHERE SUBJECT_ID" in upper:
            self.rows = [item for item in self.db.items.values() if item[1] == params[0]]
        elif "INSERT INTO CIVIC_CASE_CONSENTS" in upper:
            self.db.items[params[0]] = tuple(params)

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return list(self.rows)


class FakeTransaction:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class FakeConnection:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def transaction(self):
        return FakeTransaction()

    def cursor(self):
        return FakeCursor(self.db)


class FakeDb:
    def __init__(self):
        self.items = {}


def make_consent():
    return Consent(
        consent_id="consent-1",
        subject_id="citizen-1",
        purpose="case_submission",
        scope=("case:submit",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-09T00:00:00+00:00",
        proof_ref="proof-1",
    )


def test_postgres_consent_round_trip_and_subject_listing():
    db = FakeDb()
    repository = PostgresConsentRepository(
        connection_factory=lambda: FakeConnection(db)
    )
    consent = make_consent()

    repository.save(consent)
    assert repository.get("consent-1") == consent
    assert repository.list_for_subject("citizen-1") == [consent]
