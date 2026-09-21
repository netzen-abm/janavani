"""SQL primitives for the atomic Submission + Case boundary."""
from __future__ import annotations
import json
from src.storage.repositories.submission_case_transaction import SubmissionCaseConcurrencyError

def lock_state(cur, case_id, submission_id, event_id):
    cur.execute(
        "SELECT version FROM civic_cases WHERE case_id = %s FOR UPDATE",
        (case_id,),
    )
    case_row = cur.fetchone()
    cur.execute(
        "SELECT version, idempotency_key FROM civic_case_submissions "
        "WHERE submission_id = %s FOR UPDATE",
        (submission_id,),
    )
    submission_row = cur.fetchone()
    cur.execute(
        "SELECT event_id, case_id, event_type, occurred_at, actor_id, "
        "source_channel, source_ref, notes FROM civic_case_events WHERE event_id = %s",
        (event_id,),
    )
    return cur.fetchone(), case_row, submission_row

def persist_case(cur, case, expected_version, event):
    if not cur:
        raise RuntimeError("A database cursor is required")
    if expected_version == 0:
        cur.execute("""INSERT INTO civic_cases (
            case_id, case_type, subject, narrative, created_by, jurisdiction_json,
            related_organisation_id, related_office_id, related_official_id,
            related_representative_id, subject_claims_json, status, created_at,
            updated_at, version
        ) VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,1)""", (
            case.case_id, case.case_type.value, case.subject, case.narrative,
            case.created_by, json.dumps(case.jurisdiction, ensure_ascii=False, separators=(",", ":")),
            case.related_organisation_id, case.related_office_id,
            case.related_official_id, case.related_representative_id,
            json.dumps(case.claims, ensure_ascii=False, separators=(",", ":")),
            case.status.value, case.created_at or event.occurred_at,
            case.updated_at or event.occurred_at,
        ))
        return 1
    cur.execute("""UPDATE civic_cases SET case_type=%s, subject=%s, narrative=%s,
        created_by=%s, jurisdiction_json=%s::jsonb, related_organisation_id=%s,
        related_office_id=%s, related_official_id=%s, related_representative_id=%s,
        subject_claims_json=%s::jsonb, status=%s, updated_at=%s, version=%s
        WHERE case_id=%s AND version=%s""", (
        case.case_type.value, case.subject, case.narrative, case.created_by,
        json.dumps(case.jurisdiction, ensure_ascii=False, separators=(",", ":")),
        case.related_organisation_id, case.related_office_id,
        case.related_official_id, case.related_representative_id,
        json.dumps(case.claims, ensure_ascii=False, separators=(",", ":")),
        case.status.value, event.occurred_at, expected_version + 1,
        case.case_id, expected_version,
    ))
    if cur.rowcount != 1:
        raise SubmissionCaseConcurrencyError("Case compare-and-swap failed")
    return expected_version + 1

def persist_submission(cur, submission, expected_version):
    if expected_version == 0:
        cur.execute("""INSERT INTO civic_case_submissions (
            submission_id, case_id, destination_ref, document_ref, channel, state,
            attempted_at, submitted_at, acknowledged_at, external_reference, ack_ref,
            error_code, retry_count, version, created_at, updated_at, idempotency_key
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
            submission.submission_id, submission.case_id, submission.destination_ref,
            submission.document_ref, submission.channel, submission.state,
            submission.attempted_at, submission.submitted_at, submission.acknowledged_at,
            submission.external_reference, submission.ack_ref, submission.error_code,
            submission.retry_count, submission.version, submission.created_at,
            submission.updated_at, submission.idempotency_key,
        ))
        return submission.version
    cur.execute("""UPDATE civic_case_submissions SET case_id=%s,destination_ref=%s,
        document_ref=%s,channel=%s,state=%s,attempted_at=%s,submitted_at=%s,
        acknowledged_at=%s,external_reference=%s,ack_ref=%s,error_code=%s,
        retry_count=%s,version=%s,created_at=%s,updated_at=%s
        WHERE submission_id=%s AND version=%s""", (
        submission.case_id, submission.destination_ref, submission.document_ref,
        submission.channel, submission.state, submission.attempted_at,
        submission.submitted_at, submission.acknowledged_at,
        submission.external_reference, submission.ack_ref, submission.error_code,
        submission.retry_count, submission.version, submission.created_at,
        submission.updated_at, submission.submission_id, expected_version,
    ))
    if cur.rowcount != 1:
        raise SubmissionCaseConcurrencyError("Submission compare-and-swap failed")
    return submission.version

def persist_event(cur, event, case_version):
    cur.execute("""INSERT INTO civic_case_events (
        event_id, case_id, event_type, occurred_at, actor_id, source_channel,
        source_ref, notes, event_version, created_at
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
        event.event_id, event.case_id, event.event_type.value, event.occurred_at,
        event.actor_id, event.source_channel, event.source_ref, event.notes,
        case_version, event.occurred_at,
    ))
