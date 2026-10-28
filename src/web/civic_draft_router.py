"""Authenticated HTTP adapter for shared civic-draft previews."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, Field

from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.services.civic_draft_workflow import (
    CivicDraftPreviewRequest,
    CivicDraftPreviewWorkflow,
)

router = APIRouter(prefix="/civic/drafts", tags=["Civic Drafting"])


class CivicDraftPreviewModel(BaseModel):
    template_id: str = Field(min_length=1, max_length=80)
    issue: str = Field(min_length=1, max_length=5000)
    subject: str = Field(default="", max_length=200)
    existing_draft: str = Field(default="", max_length=8000)
    jurisdiction: str = Field(default="", max_length=300)
    requested_documents: list[str] = Field(default_factory=list, max_length=12)
    part_i_interrogatories: list[str] = Field(default_factory=list, max_length=12)
    requested_conditions: list[str] = Field(default_factory=list, max_length=12)
    remedies_reserved: list[str] = Field(default_factory=list, max_length=8)
    response_period: str | None = Field(default=None, max_length=120)
    deadline_date: str | None = Field(default=None, max_length=40)
    use_ai: bool = False
    remote_processing_consent: bool = False


@router.post("/preview")
def preview_civic_draft(
    request: CivicDraftPreviewModel,
    response: Response,
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> dict[str, object]:
    """Return an ephemeral preview; remote AI still requires verified identity."""
    context: IdentityContext | None = None
    if authorization is not None:
        context = require_authenticated_identity(authorization, request_id)
    workflow = CivicDraftPreviewWorkflow()
    try:
        result = workflow.preview(
            CivicDraftPreviewRequest(
                template_id=request.template_id,
                issue=request.issue,
                subject=request.subject,
                existing_draft=request.existing_draft,
                jurisdiction=request.jurisdiction,
                requested_documents=tuple(request.requested_documents),
                part_i_interrogatories=tuple(request.part_i_interrogatories),
                requested_conditions=tuple(request.requested_conditions),
                remedies_reserved=tuple(request.remedies_reserved),
                response_period=request.response_period,
                deadline_date=request.deadline_date,
            ),
            identity=context,
            use_ai=request.use_ai,
            remote_processing_consent=request.remote_processing_consent,
        )
    except LookupError as exc:
        raise HTTPException(status_code=422, detail="Unsupported civic document template") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return result
