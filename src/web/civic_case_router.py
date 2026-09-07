"""HTTP adapter for the shared civic case and civic action capabilities."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.capabilities.civic_case import CivicCaseCreateRequest
from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.platform.composition import (
    create_authority_repository,
    create_case_capability,
    create_case_repository,
    create_civic_action_capability,
)

router = APIRouter(prefix="/civic/cases", tags=["Civic Cases"])
_REPOSITORY = create_case_repository()
_CAPABILITY = create_case_capability(_REPOSITORY)
_CIVIC_ACTION_CAPABILITY = create_civic_action_capability(
    case_repository=_REPOSITORY,
    authority_repository=create_authority_repository(),
)


class CaseCreateRequest(BaseModel):
    case_type: CaseType
    subject: str = Field(min_length=1)
    narrative: str = Field(min_length=1)
    case_id: str | None = None
    created_by: str | None = None
    jurisdiction: dict[str, Any] = Field(default_factory=dict)
    related_organisation_id: str | None = None
    related_office_id: str | None = None
    related_official_id: str | None = None
    related_representative_id: str | None = None
    claims: list[dict[str, Any]] = Field(default_factory=list)


class ConsentRequest(BaseModel):
    consent_id: str = Field(min_length=1)


class EvidenceRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_channel: str | None = None


class EventRequest(BaseModel):
    source_channel: str | None = None
    source_ref: str | None = None
    notes: str | None = None


@router.post("")
async def create_case(request: CaseCreateRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = _CAPABILITY.create(
            CivicCaseCreateRequest(
                case_type=request.case_type, subject=request.subject, narrative=request.narrative,
                jurisdiction=request.jurisdiction, related_organisation_id=request.related_organisation_id,
                related_office_id=request.related_office_id, related_official_id=request.related_official_id,
                related_representative_id=request.related_representative_id, claims=request.claims,
            ), identity=context, source_channel="webapp",
        )
        return {"case_id": result.case.case_id, "status": result.case.status.value}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/{case_id}")
async def get_case(case_id: str, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    case = _CAPABILITY.get_owned(case_id, identity=context)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _serialize(case)


@router.get("/{case_id}/document/draft")
async def build_document_draft(case_id: str, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    """Build the same reviewable document contract used by other surfaces."""
    try:
        result = _CIVIC_ACTION_CAPABILITY.build_document(case_id, identity=context)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "case_id": result.draft.case_id,
        "document_id": result.draft.document_id,
        "document_type": result.draft.document_type,
        "date": result.draft.date,
        "subject": result.draft.subject,
        "body": result.draft.body,
        "authority_id": result.authority_id,
        "to": {"name": result.draft.to.name, "address": result.draft.to.address,
               "email": result.draft.to.email, "role": result.draft.to.role},
        "cc": [{"name": p.name, "address": p.address, "email": p.email, "role": p.role}
               for p in result.draft.cc],
        "submission": "not_submitted",
    }


@router.post("/{case_id}/consent")
async def add_consent(case_id: str, request: ConsentRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = _CAPABILITY.add_consent(case_id, request.consent_id, identity=context)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"case_id": result.case.case_id, "consent_refs": list(result.case.consent_refs)}


@router.post("/{case_id}/evidence")
async def add_evidence(case_id: str, request: EvidenceRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = _CAPABILITY.add_evidence(case_id, request.evidence_id, identity=context, source_channel=request.source_channel or "webapp")
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return _event_result(result.case, result.case.events[-1].event_type.value)


@router.post("/{case_id}/review")
async def start_review(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:start_review", request)


@router.post("/{case_id}/ready")
async def mark_ready(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:mark_ready", request)


@router.post("/{case_id}/submitting")
async def begin_submission(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:begin_submission", request)


@router.post("/{case_id}/queued")
async def queue_submission(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:queue_submission", request)


@router.post("/{case_id}/submit")
async def submit_case(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:submit", request)


@router.post("/{case_id}/acknowledge")
async def acknowledge_case(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:acknowledge", request)


def _transition(context: IdentityContext, case_id: str, action: str, request: EventRequest) -> dict[str, object]:
    try:
        result = _CAPABILITY.transition(case_id, action=action, identity=context,
                                       source_channel=request.source_channel or "webapp",
                                       source_ref=request.source_ref, notes=request.notes)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except PermissionError as exc:
        message = str(exc)
        raise HTTPException(status_code=409 if "approval" in message.lower() else 403, detail=message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _event_result(result.case, result.case.events[-1].event_type.value)


def _event_result(case: CivicCase, event_type: str) -> dict[str, object]:
    return {"case_id": case.case_id, "status": case.status.value, "event": event_type}


def _serialize(case: CivicCase) -> dict[str, object]:
    return {
        "case_id": case.case_id, "case_type": case.case_type.value, "subject": case.subject,
        "narrative": case.narrative, "created_by": case.created_by, "jurisdiction": case.jurisdiction,
        "related_organisation_id": case.related_organisation_id, "related_office_id": case.related_office_id,
        "related_official_id": case.related_official_id, "related_representative_id": case.related_representative_id,
        "claims": list(case.claims), "evidence_refs": list(case.evidence_refs),
        "document_refs": list(case.document_refs), "consent_refs": list(case.consent_refs),
        "status": case.status.value,
        "events": [{"event_id": e.event_id, "event_type": e.event_type.value, "occurred_at": e.occurred_at,
                    "actor_id": e.actor_id, "source_channel": e.source_channel,
                    "source_ref": e.source_ref, "notes": e.notes} for e in case.events],
    }
