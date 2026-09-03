from src.core.civic_case import CaseEvent, CaseEventType, CaseType, CivicCase
from src.storage.repositories.postgres_civic_case import (
    PostgresCivicCaseConcurrencyError,
    PostgresCivicCaseRepository,
)


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self._rows = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, sql, params=()):
        sql_upper = sql.upper()
        self.rowcount = 0
        if "SELECT VERSION, CREATED_AT" in sql_upper:
            case = self.db.get(params[0])
            self._rows = [
                {"version": case["version"], "created_at": case["created_at"]}
            ] if case else []
        elif "SELECT * FROM CIVIC_CASES" in sql_upper:
            case = self.db.get(params[0])
            self._rows = [case] if case else []
        elif "SELECT EVENT_ID FROM CIVIC_CASE_EVENTS" in sql_upper:
            self._rows = [
                {"event_id": item["event_id"]}
                for item in self.db.events.get(params[0], [])
            ]
        elif "SELECT * FROM CIVIC_CASE_EVENTS" in sql_upper:
            self._rows = self.db.events.get(params[0], [])
        elif "SELECT * FROM CIVIC_CASE_EVIDENCE_REFS" in sql_upper:
            self._rows = self.db.evidence.get(params[0], [])
        elif "SELECT * FROM CIVIC_CASE_DOCUMENT_REFS" in sql_upper:
            self._rows = self.db.documents.get(params[0], [])
        elif "SELECT * FROM CIVIC_CASE_CONSENTS" in sql_upper:
            self._rows = self.db.consents.get(params[0], [])
        elif "INSERT INTO CIVIC_CASES" in sql_upper:
            self.db.cases[params[0]] = {
                "case_id": params[0], "case_type": params[1],
                "subject": params[2], "narrative": params[3],
                "created_by": params[4], "jurisdiction_json": params[5],
                "related_organisation_id": params[6],
                "related_office_id": params[7],
                "related_official_id": params[8],
                "related_representative_id": params[9],
                "subject_claims_json": params[10], "status": params[11],
                "created_at": params[12], "updated_at": params[13],
                "version": params[14],
            }
            self.rowcount = 1
        elif "UPDATE CIVIC_CASES SET" in sql_upper:
            case = self.db.get(params[-2])
            expected = params[-1]
            if case and case["version"] == expected:
                fields = [
                    "case_type", "subject", "narrative", "created_by",
                    "jurisdiction_json", "related_organisation_id",
                    "related_office_id", "related_official_id",
                    "related_representative_id", "subject_claims_json",
                    "status", "created_at", "updated_at", "version",
                ]
                for name, value in zip(fields, params[:-2]):
                    case[name] = value
                self.rowcount = 1
        elif "INSERT INTO CIVIC_CASE_EVENTS" in sql_upper:
            for row in params:
                self.db.events.setdefault(row[1], []).append({
                    "event_id": row[0], "case_id": row[1],
                    "event_type": row[2], "occurred_at": row[3],
                    "actor_id": row[4], "source_channel": row[5],
                    "source_ref": row[6], "notes": row[7],
                })
        elif "INSERT INTO CIVIC_CASE_EVIDENCE_REFS" in sql_upper:
            for row in params:
                self.db.evidence.setdefault(row[0], []).append({
                    "case_id": row[0], "evidence_id": row[1],
                })
        elif "INSERT INTO CIVIC_CASE_DOCUMENT_REFS" in sql_upper:
            for row in params:
                self.db.documents.setdefault(row[0], []).append({
                    "case_id": row[0], "document_id": row[1],
                })

    def executemany(self, sql, params):
        self.execute(sql, list(params))

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


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

    def cursor(self, row_factory=None):
        return FakeCursor(self.db)


class FakeDb:
    def __init__(self):
        self.cases = {}
        self.events = {}
        self.evidence = {}
        self.documents = {}
        self.consents = {}

    def get(self, case_id):
        return self.cases.get(case_id)



def make_case():
    case = CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Road defect",
        narrative="A road needs repair.",
        created_by="citizen-1",
        evidence_refs=["evidence-1"],
        document_refs=["document-1"],
    )
    case.events.append(
        CaseEvent(
            event_id="event-1",
            case_id="case-1",
            event_type=CaseEventType.CREATED,
            occurred_at="2026-09-03T00:00:00+00:00",
        )
    )
    return case


def test_postgres_round_trip_and_versioning():
    db = FakeDb()
    repository = PostgresCivicCaseRepository(
        connection_factory=lambda: FakeConnection(db)
    )
    case = make_case()

    repository.save(case)
    assert case.version == 1
    assert repository.get("case-1").subject == "Road defect"

    case.subject = "Updated road defect"
    repository.save(case)
    assert case.version == 2
    assert repository.get("case-1").subject == "Updated road defect"


def test_postgres_rejects_stale_version():
    db = FakeDb()
    repository = PostgresCivicCaseRepository(
        connection_factory=lambda: FakeConnection(db)
    )
    case = make_case()
    repository.save(case)

    stale = make_case()
    stale.version = 1
    case.subject = "Current"
    repository.save(case)

    try:
        repository.save(stale)
    except PostgresCivicCaseConcurrencyError:
        pass
    else:
        raise AssertionError("stale version must be rejected")
