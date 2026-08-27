"""Thin FastAPI boundary over the canonical CaseWorkflowService.

This router owns transport DTOs only. Domain/application rules stay in
``src.application.case_workflow`` and provider-specific delivery stays behind
transport adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.application.case_workflow import (
    CaseWorkflowService,
    InMemoryCaseRepository,
    InMemoryEvidenceRepository,
    InMemorySubmissionRepository,
)
from src.domain.submission import Submission

router = APIRouter(prefix="/cases", tags=["Cases"])


class CreateCaseRequest(BaseModel):
    issue: str = Field(min_length=1, max_length=20_000)


class CaseResponse(BaseModel):
    case_id: str
    status: str
    issue: str
    evidence_ids: list[str]
    authority_ids: list[str]
    submission_ids: list[str]
    consent_ids: list[str]


class CreateSubmissionRequest(BaseModel):
    destination_ref: str = Field(min_length=1, max_length=500)
    consent_ref: str | None = Field(default=None, max_length=200)
    authorization_ref: str | None = Field(default=None, max_length=200)
    payload_hash: str | None = Field(default=None, max_length=256)


class SubmissionResponse(BaseModel):
    submission_id: str
    operation_id: str
    case_id: str
    destination_ref: str
    status: str
    events: list[dict[str, str | None]]


class _MissingAuthorityRepository:
    """Temporary boundary until the canonical authority persistence adapter is wired."""

    def get(self, authority_id: str):
        return None


@dataclass
class _WorkflowContainer:
    service: CaseWorkflowService


_container = _WorkflowContainer(
    service=CaseWorkflowService(
        cases=InMemoryCaseRepository(),
        evidence=InMemoryEvidenceRepository(),
        authorities=_MissingAuthorityRepository(),
        submissions=InMemorySubmissionRepository(),
    )
)


def get_workflow() -> CaseWorkflowService:
    return _container.service


Workflow = Annotated[CaseWorkflowService, Depends(get_workflow)]


def _case_response(case) -> CaseResponse:
    return CaseResponse(
        case_id=case.id,
        status=case.status.value,
        issue=case.issue,
        evidence_ids=list(case.evidence_ids),
        authority_ids=list(case.authority_ids),
        submission_ids=list(case.submission_ids),
        consent_ids=list(case.consent_ids),
    )


def _submission_response(submission: Submission) -> SubmissionResponse:
    return SubmissionResponse(
        submission_id=submission.submission_id,
        operation_id=submission.operation_id,
        case_id=submission.case_id,
        destination_ref=submission.destination_ref,
        status=submission.status.value,
        events=[
            {
                "status": event.status.value,
                "occurred_at": event.occurred_at.isoformat(),
                "adapter_id": event.adapter_id,
                "reference": event.reference,
                "reason": event.reason,
            }
            for event in submission.events
        ],
    )


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(request: CreateCaseRequest, workflow: Workflow) -> CaseResponse:
    try:
        return _case_response(workflow.create_case(request.issue, actor="api"))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, workflow: Workflow) -> CaseResponse:
    case = workflow.cases.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    return _case_response(case)


@router.post("/{case_id}/submission", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(case_id: str, request: CreateSubmissionRequest, workflow: Workflow) -> SubmissionResponse:
    try:
        submission = workflow.create_submission(
            case_id,
            request.destination_ref,
            consent_ref=request.consent_ref,
            authorization_ref=request.authorization_ref,
            payload_hash=request.payload_hash,
            actor="api",
        )
        return _submission_response(submission)
    except ValueError as exc:
        message = str(exc)
        code = 404 if message.startswith("case not found") else 409
        raise HTTPException(status_code=code, detail=message) from exc


@router.get("/{case_id}/submission/{submission_id}", response_model=SubmissionResponse)
def get_submission(case_id: str, submission_id: str, workflow: Workflow) -> SubmissionResponse:
    try:
        submission = workflow._submission(submission_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if submission.case_id != case_id:
        raise HTTPException(status_code=404, detail="submission not found")
    return _submission_response(submission)
