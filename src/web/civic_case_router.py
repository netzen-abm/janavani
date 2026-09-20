"""HTTP adapter for the shared civic case and civic action capabilities."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from src.capabilities.civic_case import CivicCaseCreateRequest
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.web.civic_case_dependencies import CAPABILITY, CIVIC_ACTION
from src.web.civic_case_document_router import router as document_router
from src.web.civic_case_lifecycle_router import router as lifecycle_router
from src.web.civic_case_models import CaseCreateRequest, ConsentRequest, EvidenceRequest, event_result, serialize_case

router = APIRouter(prefix="/civic/cases", tags=["Civic Cases"])
router.include_router(document_router)
router.include_router(lifecycle_router)

@router.post("")
async def create_case(request: CaseCreateRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = CAPABILITY.create(
            CivicCaseCreateRequest(
                case_type=request.case_type, subject=request.subject, narrative=request.narrative,
                jurisdiction=request.jurisdiction, related_organisation_id=request.related_organisation_id,
                related_office_id=request.related_office_id, related_official_id=request.related_official_id,
                related_representative_id=request.related_representative_id, claims=request.claims,
            ),
            identity=context, source_channel="webapp",
        )
        return {"case_id": result.case.case_id, "status": result.case.status.value}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

@router.get("/{case_id}")
async def get_case(case_id: str, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    case = CAPABILITY.get_owned(case_id, identity=context)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return serialize_case(case)

@router.post("/{case_id}/consent")
async def add_consent(case_id: str, request: ConsentRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = CIVIC_ACTION.add_consent(case_id, request.consent_id, identity=context)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"case_id": result.case.case_id, "consent_refs": list(result.case.consent_refs)}

@router.post("/{case_id}/evidence")
async def add_evidence(case_id: str, request: EvidenceRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        result = CIVIC_ACTION.attach_evidence(
            case_id, request.evidence_id, identity=context, source_channel=request.source_channel or "webapp"
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Evidence or case not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return event_result(result.case, result.case.events[-1].event_type.value)
