"""Review, approval, and submission-lifecycle HTTP routes."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.web.civic_case_dependencies import CAPABILITY, CIVIC_ACTION
from src.web.civic_case_models import EventRequest, event_result

router = APIRouter(tags=["Civic Cases"])

@router.post("/{case_id}/review")
async def start_review(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = CAPABILITY.start_review(case_id, identity=context)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return event_result(result.case, result.case.events[-1].event_type.value)

@router.post("/{case_id}/ready")
async def mark_ready(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = CAPABILITY.approve(case_id, identity=context)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        message = str(exc)
        status = 409 if "approval" in message.lower() or "consent" in message.lower() else 403
        raise HTTPException(status_code=status, detail=message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return event_result(result.case, result.case.events[-1].event_type.value)

@router.post("/{case_id}/submitting")
async def begin_submission(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:begin_submission", request)

@router.post("/{case_id}/queued")
async def queue_submission(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:queue_submission", request)

@router.post("/{case_id}/submit")
async def submit_case(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    raise HTTPException(status_code=409, detail="Direct case submission is disabled; use the canonical SubmissionCapability with explicit approval, consent, and a delivery transport.")

@router.post("/{case_id}/acknowledge")
async def acknowledge_case(case_id: str, request: EventRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    return _transition(context, case_id, "case:acknowledge", request)

def _transition(context: IdentityContext, case_id: str, action: str, request: EventRequest) -> dict[str, object]:
    try:
        result = CAPABILITY.transition(
            case_id, action=action, identity=context,
            source_channel=request.source_channel or "webapp",
            source_ref=request.source_ref, notes=request.notes,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except PermissionError as exc:
        message = str(exc)
        status = 409 if "approval" in message.lower() or "consent" in message.lower() else 403
        raise HTTPException(status_code=status, detail=message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return event_result(result.case, result.case.events[-1].event_type.value)
