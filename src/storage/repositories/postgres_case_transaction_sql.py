"""SQL primitives for the canonical Case transaction boundary."""
from __future__ import annotations
import json

def event_payload(event):
    return (
        event.case_id, event.event_type.value, event.occurred_at,
        event.actor_id, event.source_channel, event.source_ref, event.notes,
    )

def encode(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)

def lock_case(cur, case_id):
    cur.execute("SELECT * FROM civic_cases WHERE case_id = %s FOR UPDATE", (case_id,))
    return cur.fetchone()

def find_event(cur, event_id):
    cur.execute(
        """SELECT event_id, case_id, event_type, occurred_at, actor_id,
                  source_channel, source_ref, notes
           FROM civic_case_events WHERE event_id = %s""",
        (event_id,),
    )
    return cur.fetchone()

def insert_case(cur, case, created_at, updated_at):
    cur.execute("""INSERT INTO civic_cases (
        case_id, case_type, subject, narrative, created_by, jurisdiction_json,
        related_organisation_id, related_office_id, related_official_id,
        related_representative_id, subject_claims_json, status, created_at,
        updated_at, version
    ) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,1)""", (
        case.case_id, case.case_type.value, case.subject, case.narrative,
        case.created_by, encode(case.jurisdiction), case.related_organisation_id,
        case.related_office_id, case.related_official_id,
        case.related_representative_id, encode(case.claims), case.status.value,
        created_at, updated_at,
    ))

def update_case(cur, case, event, current_version):
    new_version = current_version + 1
    cur.execute("""UPDATE civic_cases SET case_type=%s, subject=%s,
        narrative=%s, created_by=%s, jurisdiction_json=%s::jsonb,
        related_organisation_id=%s, related_office_id=%s,
        related_official_id=%s, related_representative_id=%s,
        subject_claims_json=%s::jsonb, status=%s, updated_at=%s, version=%s
        WHERE case_id=%s AND version=%s""", (
        case.case_type.value, case.subject, case.narrative, case.created_by,
        encode(case.jurisdiction), case.related_organisation_id,
        case.related_office_id, case.related_official_id,
        case.related_representative_id, encode(case.claims), case.status.value,
        event.occurred_at, new_version, case.case_id, current_version,
    ))
    return new_version

def insert_event(cur, event, version):
    cur.execute("""INSERT INTO civic_case_events (
        event_id, case_id, event_type, occurred_at, actor_id,
        source_channel, source_ref, notes, event_version, created_at
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
        event.event_id, event.case_id, event.event_type.value, event.occurred_at,
        event.actor_id, event.source_channel, event.source_ref, event.notes,
        version, event.occurred_at,
    ))
