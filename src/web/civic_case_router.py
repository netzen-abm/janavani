"""Thin HTTP adapter for the shared civic case contract.

The adapter depends on the canonical repository boundary. The default
repository is process-local until a production durable provider is verified.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core.civic_case import CaseType, CivicCase
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository

router = APIRouter(prefix="/civic/cases", tags=["Civic Cases"])


class CaseCreateRequest(BaseModel):
    case_id: str = Field(min_length=1)
    case_type: CaseType
    subject: str = Field(min_length=1)
    narrative: str = Field(min_length=1)
    created_by: str | None = None
    related_office_id: str | None = None


class ConsentRequest(BaseModel):
    consent_id: str = Field(min_length=1)


class EvidenceRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    occurred_at: str = Field(min_length=1)
    actor_id: str | None = None
    source_channel: str | None = None


class EventRequest(BaseModel):
    event_id: str = Field(min_length=1)
    occurred_at: str = Field(min_length=1)
    actor_id: str | None = None
    source_channel: str | None = None
    notes: str | None = None


_CASES: dict[str, CivicCase] = {}
_REPOSITORY = InMemoryCivicCaseRepository(_CASES)


@router.post("")
async def create_case(request: CaseCreateRequest) -> dict[str, object]:
    if _REPOSITORY.get(request.case_id) is not None:
        raise HTTPException(status_code=409, detail="Case already exists")
    case = CivicCase(
        case_id=request.case_id,
        case_type=request.case_type,
        subject=request.subject,
        narrative=request.narrative,
        created_by=request.created_by,
        related_office_id=request.related_office_id,
    )
    _REPOSITORY.save(case)
    return {"case_id": case.case_id, "status": case.status.value}


@router.get("/{case_id}")
async def get_case(case_id: str) -> dict[str, object]:
    return _serialize(_get_case(case_id))


@router.post("/{case_id}/consent")
async def add_consent(case_id: str, request: ConsentRequest) -> dict[str, object]:
    case = _get_case(case_id)
    if request.consent_id not in case.consent_refs:
        case.consent_refs.append(request.consent_id)
    _REPOSITORY.save(case)
    return {"case_id": case.case_id, "consent_refs": list(case.consent_refs)}


@router.post("/{case_id}/review")
async def start_review(case_id: str, request: EventRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.start_review(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=request.actor_id,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/ready")
async def mark_ready(case_id: str, request: EventRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.mark_ready(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=request.actor_id,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/evidence")
async def add_evidence(case_id: str, request: EvidenceRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.add_evidence(
        request.evidence_id,
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=request.actor_id,
        source_channel=request.source_channel,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/submitting")
async def begin_submission(case_id: str, request: EventRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.begin_submission(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=request.actor_id,
        source_channel=request.source_channel,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/queued")
async def queue_submission(case_id: str, request: EventRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.queue_submission(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=request.actor_id,
        source_channel=request.source_channel,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/submit")
async def submit_case(case_id: str, request: EventRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.submit(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=request.actor_id,
        source_channel=request.source_channel,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/acknowledge")
async def acknowledge_case(case_id: str, request: EventRequest) -> dict[str, object]:
    case = _get_case(case_id)
    event = case.acknowledge(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        source_channel=request.source_channel,
        notes=request.notes,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


def _get_case(case_id: str) -> CivicCase:
    case = _REPOSITORY.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


def _event_result(case: CivicCase, event_type: str) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "status": case.status.value,
        "event": event_type,
    }


def _serialize(case: CivicCase) -> dict[str, object]:
    return {
        "case_id": case.case_id,
        "case_type": case.case_type.value,
        "subject": case.subject,
        "narrative": case.narrative,
        "created_by": case.created_by,
        "related_office_id": case.related_office_id,
        "evidence_refs": list(case.evidence_refs),
        "document_refs": list(case.document_refs),
        "consent_refs": list(case.consent_refs),
        "status": case.status.value,
        "events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "occurred_at": event.occurred_at,
                "actor_id": event.actor_id,
                "source_channel": event.source_channel,
                "notes": event.notes,
            }
            for event in case.events
        ],
    }
