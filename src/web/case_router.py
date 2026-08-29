"""Independent WebApp case endpoints backed by the shared case capability."""
from fastapi import APIRouter, HTTPException

from src.domain.case import CaseCreate, CaseStatus, CaseUpdate
from src.services.case_service import CaseService

router = APIRouter(prefix="/api/v1/cases", tags=["Civic Cases"])
_service = CaseService()


@router.post("", status_code=201)
def create_case(payload: CaseCreate):
    return _service.create_case(payload)


@router.get("")
def list_cases():
    return {"items": _service.list_cases()}


@router.get("/{case_id}")
def get_case(case_id: str):
    case = _service.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}")
def update_case(case_id: str, payload: CaseUpdate):
    case = _service.update_case(case_id, payload)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/status/{status}")
def transition_case(case_id: str, status: CaseStatus):
    case = _service.transition(case_id, status)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
