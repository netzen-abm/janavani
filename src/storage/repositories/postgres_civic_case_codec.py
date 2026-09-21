"""Domain/row mapping for the PostgreSQL Civic Case provider."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any
from src.core.civic_case import CaseEvent, CaseEventType, CaseStatus, CaseType, CivicCase

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def encode(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)

def decode(value: Any, default: Any) -> Any:
    if value is None:
        return default
    return json.loads(value) if isinstance(value, str) else value

def case_values(case, *, created_at: str, updated_at: str, version: int):
    return (
        case.case_id, case.case_type.value, case.subject, case.narrative,
        case.created_by, encode(case.jurisdiction), case.related_organisation_id,
        case.related_office_id, case.related_official_id,
        case.related_representative_id, encode(case.claims), case.status.value,
        created_at, updated_at, version,
    )

def event_values(event):
    return (
        event.event_id, event.case_id, event.event_type.value, event.occurred_at,
        event.actor_id, event.source_channel, event.source_ref, event.notes, 1, now(),
    )

def hydrate(row, events, evidence, documents, consents) -> CivicCase:
    return CivicCase(
        case_id=str(row["case_id"]), case_type=CaseType(row["case_type"]),
        subject=str(row["subject"]), narrative=str(row["narrative"]),
        created_by=row.get("created_by"),
        jurisdiction=decode(row.get("jurisdiction_json"), {}),
        related_organisation_id=row.get("related_organisation_id"),
        related_office_id=row.get("related_office_id"),
        related_official_id=row.get("related_official_id"),
        related_representative_id=row.get("related_representative_id"),
        claims=decode(row.get("subject_claims_json"), []),
        evidence_refs=[str(x["evidence_id"]) for x in evidence],
        document_refs=[str(x["document_id"]) for x in documents],
        consent_refs=[str(x["consent_id"]) for x in consents],
        status=CaseStatus(row["status"]),
        events=[CaseEvent(
            event_id=str(x["event_id"]), case_id=str(x["case_id"]),
            event_type=CaseEventType(x["event_type"]),
            occurred_at=str(x["occurred_at"]), actor_id=x.get("actor_id"),
            source_channel=x.get("source_channel"), source_ref=x.get("source_ref"),
            notes=x.get("notes"),
        ) for x in events],
        created_at=row.get("created_at"), updated_at=row.get("updated_at"),
        version=int(row.get("version", 1)),
    )
