"""HTTP adapter for the shared civic case capability.

The router is deliberately thin: authentication is resolved by the canonical
identity boundary, authorization is evaluated by the shared authorization
kernel, and persistence is delegated to the canonical case repository.
"""
from __future__ import annotations

import os
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.provider import create_civic_case_repository

router = APIRouter(prefix="/civic/cases", tags=["Civic Cases"])


class CaseCreateRequest(BaseModel):
    case_id: str = Field(min_length=1)
    case_type: CaseType
    subject: str = Field(min_length=1)
    narrative: str = Field(min_length=1)
    # Deprecated compatibility input. The authenticated principal is authoritative.
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
    event_id: str = Field(min_length=1)
    occurred_at: str = Field(min_length=1)
    actor_id: str | None = None
    source_channel: str | None = None


class EventRequest(BaseModel):
    event_id: str = Field(min_length=1)
    occurred_at: str = Field(min_length=1)
    actor_id: str | None = None
    source_channel: str | None = None
    source_ref: str | None = None
    notes: str | None = None


_CASES: dict[str, CivicCase] = {}


def _create_repository():
    provider = os.getenv("JANAVANI_CASE_REPOSITORY_PROVIDER", "memory").strip().lower()
    if provider == "memory":
        return InMemoryCivicCaseRepository(_CASES)
    return create_civic_case_repository(provider)


_REPOSITORY = _create_repository()


def _authorize(
    context: IdentityContext,
    *,
    capability: str,
    action: str,
    case: CivicCase | None = None,
    high_risk: bool = False,
) -> None:
    if case is not None and case.created_by != context.principal.principal_id:
        # Do not reveal the existence of another principal's case.
        raise HTTPException(status_code=404, detail="Case not found")

    decision = authorize(
        AuthorizationRequest(
            context=context,
            capability=capability,
            action=action,
            resource_id=case.case_id if case else None,
            risk_level="high" if high_risk else "normal",
            requires_approval=high_risk,
        )
    )
    if decision == AuthorizationDecision.DENY:
        raise HTTPException(status_code=403, detail="Capability not authorized")
    if decision == AuthorizationDecision.REQUIRE_APPROVAL:
        raise HTTPException(status_code=409, detail="Explicit approval required")


@router.post("")
async def create_case(
    request: CaseCreateRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    _authorize(context, capability="case:write", action="case:create")
    if _REPOSITORY.get(request.case_id) is not None:
        raise HTTPException(status_code=409, detail="Case already exists")

    principal_id = context.principal.principal_id
    case = CivicCase(
        case_id=request.case_id,
        case_type=request.case_type,
        subject=request.subject,
        narrative=request.narrative,
        created_by=principal_id,
        jurisdiction=request.jurisdiction,
        related_organisation_id=request.related_organisation_id,
        related_office_id=request.related_office_id,
        related_official_id=request.related_official_id,
        related_representative_id=request.related_representative_id,
        claims=request.claims,
    )
    _REPOSITORY.save(case)
    return {"case_id": case.case_id, "status": case.status.value}


@router.get("/{case_id}")
async def get_case(
    case_id: str,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    case = _get_case(case_id)
    _authorize(context, capability="case:read", action="case:read", case=case)
    return _serialize(case)


@router.post("/{case_id}/consent")
async def add_consent(
    case_id: str,
    request: ConsentRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    case = _get_case(case_id)
    _authorize(context, capability="case:write", action="case:consent", case=case)
    if request.consent_id not in case.consent_refs:
        case.consent_refs.append(request.consent_id)
    _REPOSITORY.save(case)
    return {"case_id": case.case_id, "consent_refs": list(case.consent_refs)}


@router.post("/{case_id}/review")
async def start_review(
    case_id: str,
    request: EventRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    return _transition(context, case_id, request, "case:review", "case:start_review", CivicCase.start_review)


@router.post("/{case_id}/ready")
async def mark_ready(
    case_id: str,
    request: EventRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    return _transition(context, case_id, request, "case:write", "case:mark_ready", CivicCase.mark_ready)


@router.post("/{case_id}/evidence")
async def add_evidence(
    case_id: str,
    request: EvidenceRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    case = _get_case(case_id)
    _authorize(context, capability="case:evidence", action="case:add_evidence", case=case)
    event = case.add_evidence(
        request.evidence_id,
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=context.principal.principal_id,
        source_channel=request.source_channel,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


@router.post("/{case_id}/submitting")
async def begin_submission(
    case_id: str,
    request: EventRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    return _transition(context, case_id, request, "case:submit", "case:begin_submission", CivicCase.begin_submission)


@router.post("/{case_id}/queued")
async def queue_submission(
    case_id: str,
    request: EventRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    return _transition(context, case_id, request, "case:submit", "case:queue_submission", CivicCase.queue_submission)


@router.post("/{case_id}/submit")
async def submit_case(
    case_id: str,
    request: EventRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    return _transition(
        context,
        case_id,
        request,
        "case:submit",
        "case:submit",
        CivicCase.submit,
        high_risk=True,
    )


@router.post("/{case_id}/acknowledge")
async def acknowledge_case(
    case_id: str,
    request: EventRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    case = _get_case(case_id)
    _authorize(context, capability="case:write", action="case:acknowledge", case=case)
    event = case.acknowledge(
        event_id=request.event_id,
        occurred_at=request.occurred_at,
        actor_id=context.principal.principal_id,
        source_channel=request.source_channel,
        source_ref=request.source_ref,
        notes=request.notes,
    )
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


def _transition(
    context: IdentityContext,
    case_id: str,
    request: EventRequest,
    capability: str,
    action: str,
    transition: Callable[..., Any],
    *,
    high_risk: bool = False,
) -> dict[str, object]:
    case = _get_case(case_id)
    _authorize(context, capability=capability, action=action, case=case, high_risk=high_risk)

    kwargs: dict[str, object] = {
        "event_id": request.event_id,
        "occurred_at": request.occurred_at,
        "actor_id": context.principal.principal_id,
    }
    if action in {"case:begin_submission", "case:queue_submission", "case:submit"}:
        kwargs["source_channel"] = request.source_channel

    event = transition(case, **kwargs)
    _REPOSITORY.save(case)
    return _event_result(case, event.event_type.value)


def _get_case(case_id: str) -> CivicCase:
    case = _REPOSITORY.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


def _event_result(case: CivicCase, event_type: str) -> dict[str, object]:
    return {"case_id": case.case_id, "status": case.status.value, "event": event_type}


def _serialize(case: CivicCase) -> dict[str, object]:
    return {
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
        "claims": list(case.claims),
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
                "source_ref": event.source_ref,
                "notes": event.notes,
            }
            for event in case.events
        ],
    }
