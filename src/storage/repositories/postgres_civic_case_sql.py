"""SQL persistence primitives for the PostgreSQL Civic Case provider."""
from __future__ import annotations
from src.storage.repositories.postgres_civic_case_codec import case_values, event_values, encode, now
from src.storage.repositories.postgres_civic_case import PostgresCivicCaseConcurrencyError

def select_children(cur, table: str, case_id: str):
    order = " ORDER BY occurred_at, event_id" if table == "civic_case_events" else ""
    cur.execute(f"SELECT * FROM {table} WHERE case_id = %s{order}", (case_id,))
    return list(cur.fetchall())

def insert_case(cur, case, created_at, updated_at, version):
    cur.execute("""INSERT INTO civic_cases (
        case_id, case_type, subject, narrative, created_by, jurisdiction_json,
        related_organisation_id, related_office_id, related_official_id,
        related_representative_id, subject_claims_json, status, created_at,
        updated_at, version
    ) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s)""",
        case_values(case, created_at=created_at, updated_at=updated_at, version=version))

def update_case(cur, case, created_at, updated_at, version, current_version):
    cur.execute("""UPDATE civic_cases SET case_type=%s, subject=%s, narrative=%s,
        created_by=%s, jurisdiction_json=%s::jsonb, related_organisation_id=%s,
        related_office_id=%s, related_official_id=%s, related_representative_id=%s,
        subject_claims_json=%s::jsonb, status=%s, created_at=%s, updated_at=%s,
        version=%s WHERE case_id=%s AND version=%s""", (
        case.case_type.value, case.subject, case.narrative, case.created_by,
        encode(case.jurisdiction), case.related_organisation_id,
        case.related_office_id, case.related_official_id,
        case.related_representative_id, encode(case.claims), case.status.value,
        created_at, updated_at, version, case.case_id, current_version))
    if cur.rowcount != 1:
        raise PostgresCivicCaseConcurrencyError(f"Stale CivicCase version for {case.case_id}")

def persist_events(cur, case):
    cur.execute("SELECT event_id FROM civic_case_events WHERE case_id = %s", (case.case_id,))
    existing = {str(x["event_id"]) for x in cur.fetchall()}
    pending = [event_values(e) for e in case.events if e.event_id not in existing]
    if pending:
        cur.executemany("""INSERT INTO civic_case_events (
            event_id, case_id, event_type, occurred_at, actor_id, source_channel,
            source_ref, notes, event_version, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", pending)

def persist_refs(cur, case):
    if case.evidence_refs:
        cur.executemany("""INSERT INTO civic_case_evidence_refs
            (case_id,evidence_id,relationship,created_at) VALUES (%s,%s,%s,%s)
            ON CONFLICT (case_id,evidence_id,relationship) DO NOTHING""",
            [(case.case_id, x, "case_evidence", now()) for x in case.evidence_refs])
    if case.document_refs:
        cur.executemany("""INSERT INTO civic_case_document_refs
            (case_id,document_id,relationship,version,created_at) VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (case_id,document_id,relationship) DO NOTHING""",
            [(case.case_id, x, "case_document", 1, now()) for x in case.document_refs])
