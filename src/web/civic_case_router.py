"""HTTP adapter for the shared civic case domain contracts."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core.civic_authority import AuthorityCandidate, AuthorityConfidence, resolve_authority
from src.core.civic_case import CaseStatus, CaseType, CivicCase
from src.core.civic_document import CivicDocument, PartyRef
from src.core.civic_evidence import EvidenceObject, EvidenceStatus, validate_evidence

router = APIRouter(prefix="/civic/cases", tags=["Civic Cases"])

_CASES: dict[str, CivicCase] = {}
_DOCUMENTS: dict[str, CivicDocument] = {}


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
    storage_ref: str = Field(min_length=1)
    sha256: str = Field(min_length=64, max_length=64)
    evidence_type: str = Field(min_length=1)
    access_policy_ref: str = Field(min_length=1)
    owner_id: str | None = None
    source_description: str | None = None


class AuthorityRequest(BaseModel):
    office_id: str = Field(min_length=1)
    confidence: AuthorityConfidence
    organisation_id: str | None = None
    source_ref: str | None = None
    rationale: str | None = None


class DocumentCreateRequest(BaseModel):
    document_id: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    language: str = Field(min_length=1)
    to_name: str = Field(min_length=1)
    to_party_type: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)


@router.post("")
async def create_case(request: CaseCreateRequest) -> dict[str, object]:
    if request.case_id in _CASES:
        raise HTTPException(status_code=409, detail="Case already exists")
    case = CivicCase(
        case_id=request.case_id,
        case_type=request.case_type,
        subject=request.subject,
        narrative=request.narrative,
        created_by=request.created_by,
        related_office_id=request.related_office_id,
    )
    _CASES[case.case_id] = case
    return {"case_id": case.case_id, "status": case.status.value}


@router.get("/{case_id}")
async def get_case(case_id: str) -> dict[str, object]:
    return _serialize(_get_case(case_id))


@router.post("/{case_id}/consent")
async def add_consent(case_id: str, request: ConsentRequest) -> dict[str, object]:
    case = _get_case(case_id)
    if request.consent_id not in case.consent_refs:
        case.consent_refs.append(request.consent_id)
    return {"case_id": case.case_id, "consent_refs": list(case.consent_refs)}


@router.post("/{case_id}/authority")
async def resolve_case_authority(case_id: str, request: AuthorityRequest) -> dict[str, object]:
    case = _get_case(case_id)
    candidate = AuthorityCandidate(
        office_id=request.office_id,
        organisation_id=request.organisation_id,
        confidence=request.confidence,
        source_ref=request.source_ref,
        rationale=request.rationale,
    )
    resolution = resolve_authority(case.case_id, [candidate])
    if resolution.selected_office_id:
        case.related_office_id = resolution.selected_office_id
    return {
        "case_id": case.case_id,
        "selected_office_id": resolution.selected_office_id,
        "verified": resolution.verified,
        "candidates": [c.office_id for c in resolution.candidates],
    }


@router.post("/{case_id}/evidence")
async def add_evidence(case_id: str, request: EvidenceRequest) -> dict[str, object]:
    case = _get_case(case_id)
    evidence = EvidenceObject(
        evidence_id=request.evidence_id,
        storage_ref=request.storage_ref,
        sha256=request.sha256,
        evidence_type=request.evidence_type,
        access_policy_ref=request.access_policy_ref,
        owner_id=request.owner_id,
        source_description=request.source_description,
        status=EvidenceStatus.ACTIVE,
    )
    try:
        validate_evidence(evidence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if evidence.evidence_id not in case.evidence_refs:
        case.evidence_refs.append(evidence.evidence_id)
    return {"case_id": case.case_id, "evidence_id": evidence.evidence_id, "status": evidence.status.value}


@router.post("/{case_id}/documents")
async def create_document(case_id: str, request: DocumentCreateRequest) -> dict[str, object]:
    case = _get_case(case_id)
    if request.document_id in _DOCUMENTS:
        raise HTTPException(status_code=409, detail="Document already exists")
    document = CivicDocument(
        document_id=request.document_id,
        document_type=request.document_type,
        title=request.title,
        language=request.language,
        to_party=PartyRef(request.to_party_type, request.to_name),
        subject=request.subject,
        body=request.body,
    )
    _DOCUMENTS[document.document_id] = document
    case.document_refs.append(document.document_id)
    return {"case_id": case.case_id, "document_id": document.document_id, "status": document.status.value}


@router.post("/{case_id}/documents/{document_id}/approve")
async def approve_document(case_id: str, document_id: str) -> dict[str, object]:
    case = _get_case(case_id)
    document = _get_document(document_id)
    if document_id not in case.document_refs:
        raise HTTPException(status_code=404, detail="Document is not attached to case")
    try:
        document.approve()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"document_id": document.document_id, "status": document.status.value}


@router.post("/{case_id}/ready")
async def mark_ready(case_id: str) -> dict[str, object]:
    case = _get_case(case_id)
    if not case.subject.strip() or not case.narrative.strip():
        raise HTTPException(status_code=422, detail="Case requires subject and narrative")
    if not case.consent_refs:
        raise HTTPException(status_code=403, detail="Submission consent is required")
    case.status = CaseStatus.READY
    return {"case_id": case.case_id, "status": case.status.value}


@router.post("/{case_id}/submit")
async def submit_case(case_id: str) -> dict[str, object]:
    case = _get_case(case_id)
    if case.status is not CaseStatus.READY:
        raise HTTPException(status_code=409, detail="Only a ready case can be submitted")
    case.status = CaseStatus.SUBMITTED
    return {"case_id": case.case_id, "status": case.status.value, "acknowledged": False}


def _get_case(case_id: str) -> CivicCase:
    case = _CASES.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


def _get_document(document_id: str) -> CivicDocument:
    document = _DOCUMENTS.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


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
    }
