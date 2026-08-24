"""Canonical HTTP adapter for the shared civic case contracts."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from src.core.civic_authority import AuthorityCandidate, AuthorityConfidence, resolve_authority
from src.core.civic_case import CaseType, CivicCase
from src.core.civic_document import CivicDocument, PartyRef
from src.core.civic_evidence import EvidenceObject, EvidenceStatus, validate_evidence
from src.storage.repositories.civic_case_repository import InMemoryCivicCaseRepository

router = APIRouter(prefix="/civic/cases", tags=["Civic Cases"])
_CASE_REPOSITORY = InMemoryCivicCaseRepository()
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


class AuthorityRequest(BaseModel):
    office_id: str = Field(min_length=1)
    confidence: AuthorityConfidence
    organisation_id: str | None = None
    source_ref: str | None = None
    rationale: str | None = None


class EvidenceRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    storage_ref: str = Field(min_length=1)
    sha256: str = Field(min_length=64, max_length=64)
    evidence_type: str = Field(min_length=1)
    access_policy_ref: str = Field(min_length=1)
    owner_id: str | None = None
    source_description: str | None = None


class DocumentCreateRequest(BaseModel):
    document_id: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    language: str = Field(min_length=1)
    to_name: str = Field(min_length=1)
    to_party_type: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)


def _policy(policy_ref: str | None) -> str:
    if not policy_ref or not policy_ref.strip():
        raise HTTPException(status_code=400, detail="X-Access-Policy-Ref is required")
    return policy_ref.strip()


def _get_case(case_id: str, policy_ref: str | None) -> CivicCase:
    policy = _policy(policy_ref)
    try:
        case = _CASE_REPOSITORY.get(case_id, access_policy_ref=policy)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


def _save(case: CivicCase, policy_ref: str | None) -> None:
    try:
        _CASE_REPOSITORY.save(case, access_policy_ref=_policy(policy_ref))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("")
async def create_case(request: CaseCreateRequest, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    policy = _policy(x_access_policy_ref)
    case = CivicCase(**request.model_dump())
    try:
        _CASE_REPOSITORY.create(case, access_policy_ref=policy)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"case_id": case.case_id, "status": case.status.value}


@router.get("/{case_id}")
async def get_case(case_id: str, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    return _serialize(_get_case(case_id, x_access_policy_ref))


@router.post("/{case_id}/consent")
async def add_consent(case_id: str, request: ConsentRequest, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    if request.consent_id not in case.consent_refs:
        case.consent_refs.append(request.consent_id)
    _save(case, x_access_policy_ref)
    return {"case_id": case.case_id, "consent_refs": list(case.consent_refs)}


@router.post("/{case_id}/authority")
async def resolve_case_authority(case_id: str, request: AuthorityRequest, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    resolution = resolve_authority(case.case_id, [AuthorityCandidate(**request.model_dump())])
    if resolution.selected_office_id:
        case.related_office_id = resolution.selected_office_id
        _save(case, x_access_policy_ref)
    return {"case_id": case.case_id, "selected_office_id": resolution.selected_office_id, "verified": resolution.verified}


@router.post("/{case_id}/evidence")
async def add_evidence(case_id: str, request: EvidenceRequest, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    evidence = EvidenceObject(**request.model_dump(), status=EvidenceStatus.ACTIVE)
    try:
        validate_evidence(evidence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if evidence.evidence_id not in case.evidence_refs:
        case.evidence_refs.append(evidence.evidence_id)
        _save(case, x_access_policy_ref)
    return {"case_id": case.case_id, "evidence_id": evidence.evidence_id, "status": evidence.status.value}


@router.post("/{case_id}/documents")
async def create_document(case_id: str, request: DocumentCreateRequest, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    if request.document_id in _DOCUMENTS:
        raise HTTPException(status_code=409, detail="Document already exists")
    document = CivicDocument(
        document_id=request.document_id, document_type=request.document_type, title=request.title,
        language=request.language, to_party=PartyRef(request.to_party_type, request.to_name),
        subject=request.subject, body=request.body,
    )
    _DOCUMENTS[document.document_id] = document
    case.document_refs.append(document.document_id)
    _save(case, x_access_policy_ref)
    return {"case_id": case.case_id, "document_id": document.document_id, "status": document.status.value}


@router.post("/{case_id}/documents/{document_id}/approve")
async def approve_document(case_id: str, document_id: str, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    document = _DOCUMENTS.get(document_id)
    if document is None or document_id not in case.document_refs:
        raise HTTPException(status_code=404, detail="Document not found on case")
    document.approve()
    return {"document_id": document.document_id, "status": document.status.value}


@router.post("/{case_id}/ready")
async def mark_ready(case_id: str, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    try:
        event = case.mark_ready(event_id=f"ready:{case_id}", occurred_at="api")
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _save(case, x_access_policy_ref)
    return {"case_id": case.case_id, "status": case.status.value, "event": event.event_type.value}


@router.post("/{case_id}/submit")
async def submit_case(case_id: str, x_access_policy_ref: str | None = Header(default=None)) -> dict[str, object]:
    case = _get_case(case_id, x_access_policy_ref)
    try:
        event = case.submit(event_id=f"submit:{case_id}", occurred_at="api", source_channel="canonical_api")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    _save(case, x_access_policy_ref)
    return {"case_id": case.case_id, "status": case.status.value, "event": event.event_type.value, "acknowledged": False}


def _serialize(case: CivicCase) -> dict[str, object]:
    return {
        "case_id": case.case_id, "case_type": case.case_type.value, "subject": case.subject,
        "narrative": case.narrative, "created_by": case.created_by, "related_office_id": case.related_office_id,
        "evidence_refs": list(case.evidence_refs), "document_refs": list(case.document_refs),
        "consent_refs": list(case.consent_refs), "status": case.status.value,
        "events": [{"event_id": e.event_id, "event_type": e.event_type.value, "occurred_at": e.occurred_at} for e in case.events],
    }
