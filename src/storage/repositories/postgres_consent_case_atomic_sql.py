"""PostgreSQL statements for atomic consent/Case persistence.

Keep SQL and row shapes here; transaction ordering and consent invariants remain
in PostgresConsentCaseAtomicRepository.
"""
from __future__ import annotations

import json

from src.core.consent import Consent


def select_action(cursor, principal_id: str, fingerprint: str):
    cursor.execute(
        """SELECT consent_id, subject_id, purpose, scope, grant_type, status,
                  created_at, expires_at, revoked_at, proof_ref, case_id
             FROM civic_case_consents
            WHERE subject_id=%s AND action_fingerprint=%s
            FOR UPDATE""",
        (principal_id, fingerprint),
    )
    return cursor.fetchone()


def lock_case(cursor, case_id: str):
    cursor.execute(
        "SELECT created_by, version FROM civic_cases WHERE case_id=%s FOR UPDATE",
        (case_id,),
    )
    return cursor.fetchone()


def select_consent(cursor, consent_id: str):
    cursor.execute(
        """SELECT consent_id, subject_id, purpose, scope, grant_type, status,
                  created_at, expires_at, revoked_at, proof_ref, case_id
             FROM civic_case_consents WHERE consent_id=%s FOR UPDATE""",
        (consent_id,),
    )
    return cursor.fetchone()


def insert_action_consent(cursor, consent: Consent, case_id: str,
                          principal_id: str, fingerprint: str):
    cursor.execute(
        """INSERT INTO civic_case_consents (
            consent_id, case_id, purpose, scope, grant_type, status,
            granted_by, subject_id, created_at, expires_at, revoked_at,
            proof_ref, action_fingerprint
        ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT DO NOTHING RETURNING consent_id""",
        (consent.consent_id, case_id, consent.purpose,
         json.dumps(list(consent.scope)), consent.grant_type.value,
         consent.status.value, principal_id, consent.subject_id,
         consent.created_at, consent.expires_at, consent.revoked_at,
         consent.proof_ref, fingerprint),
    )
    return cursor.fetchone()


def insert_attached_consent(cursor, consent: Consent, case_id: str,
                            principal_id: str) -> None:
    cursor.execute(
        """INSERT INTO civic_case_consents (
            consent_id, case_id, purpose, scope, grant_type, status,
            granted_by, subject_id, created_at, expires_at, revoked_at, proof_ref
        ) VALUES (%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (consent_id) DO NOTHING""",
        (consent.consent_id, case_id, consent.purpose,
         json.dumps(list(consent.scope)), consent.grant_type.value,
         consent.status.value, principal_id, consent.subject_id,
         consent.created_at, consent.expires_at, consent.revoked_at,
         consent.proof_ref),
    )


def attach_existing_consent_to_case(cursor, consent_id: str, case_id: str,
                                    principal_id: str) -> None:
    cursor.execute(
        """UPDATE civic_case_consents SET case_id=%s
             WHERE consent_id=%s AND subject_id=%s AND case_id IS NULL""",
        (case_id, consent_id, principal_id),
    )


def select_event(cursor, event_id: str, case_id: str):
    cursor.execute(
        """SELECT event_type, actor_id, source_ref, notes
             FROM civic_case_events WHERE event_id=%s AND case_id=%s""",
        (event_id, case_id),
    )
    return cursor.fetchone()


def update_case(cursor, case, expected_version: int, new_version: int) -> None:
    cursor.execute(
        """UPDATE civic_cases SET status=%s, updated_at=%s, version=%s
             WHERE case_id=%s AND version=%s""",
        (case.status.value, case.updated_at, new_version,
         case.case_id, expected_version),
    )


def insert_consent_event(cursor, event_id: str, case_id: str, consent: Consent,
                         principal_id: str, new_version: int) -> None:
    cursor.execute(
        """INSERT INTO civic_case_events (
            event_id, case_id, event_type, occurred_at, actor_id,
            source_channel, source_ref, notes, event_version, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (event_id, case_id, "consent_recorded", consent.created_at,
         principal_id, None, consent.proof_ref, consent.purpose,
         new_version, consent.created_at),
    )
