import json
from pathlib import Path

from src.core.civic_case import CaseEventType, CaseStatus, CaseType, CivicCase


FIXTURE = Path(__file__).parent / "fixtures" / "civic_case_serialization.json"


def test_canonical_fixture_round_trips_through_python_model():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    case = CivicCase(
        case_id=payload["case_id"],
        case_type=CaseType(payload["case_type"]),
        subject=payload["subject"],
        narrative=payload["narrative"],
        created_by=payload["created_by"],
        jurisdiction=payload["jurisdiction"],
        related_organisation_id=payload["related_organisation_id"],
        related_office_id=payload["related_office_id"],
        related_official_id=payload["related_official_id"],
        related_representative_id=payload["related_representative_id"],
        claims=payload["claims"],
        evidence_refs=payload["evidence_refs"],
        document_refs=payload["document_refs"],
        consent_refs=payload["consent_refs"],
        status=CaseStatus(payload["status"]),
        events=[],
        created_at=payload["created_at"],
        updated_at=payload["updated_at"],
        version=payload["version"],
    )
    for event in payload["events"]:
        case.events.append(
            __import__("src.core.civic_case", fromlist=["CaseEvent"]).CaseEvent(
                event_id=event["event_id"],
                case_id=event["case_id"],
                event_type=CaseEventType(event["event_type"]),
                occurred_at=event["occurred_at"],
                actor_id=event["actor_id"],
                source_channel=event["source_channel"],
                source_ref=event["source_ref"],
                notes=event["notes"],
            )
        )

    encoded = {
        "case_id": case.case_id,
        "case_type": case.case_type.value,
        "subject": case.subject,
        "narrative": case.narrative,
        "created_by": case.created_by,
        "jurisdiction": case.jurisdiction,
        "related_organisation_id": case.related_organisation_id,
        "related_office_id": case.related_office_id,
        "related_official_id": case.related_official_id,
        "related_representative_id": case.related_representative_id,
        "claims": case.claims,
        "evidence_refs": case.evidence_refs,
        "document_refs": case.document_refs,
        "consent_refs": case.consent_refs,
        "status": case.status.value,
        "events": [
            {
                "event_id": event.event_id,
                "case_id": event.case_id,
                "event_type": event.event_type.value,
                "occurred_at": event.occurred_at,
                "actor_id": event.actor_id,
                "source_channel": event.source_channel,
                "source_ref": event.source_ref,
                "notes": event.notes,
            }
            for event in case.events
        ],
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "version": case.version,
    }

    assert encoded == payload
