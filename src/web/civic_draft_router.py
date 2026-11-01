"""Authenticated HTTP adapter for shared civic-draft previews."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Response

from src.access.citizen_document_format_policy import require_format_permission
from pydantic import BaseModel, Field

from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.storage.repositories.citizen_document_format_provider import CitizenDocumentFormatProviderConfigurationError
from src.platform.composition import create_citizen_document_format_repository
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
    preview_processing_consent: bool = False
    use_ai: bool = False
    remote_processing_consent: bool = False
    saved_format_id: str | None = Field(default=None, max_length=80)


@router.post("/preview")
def preview_civic_draft(
    request: CivicDraftPreviewModel,
    response: Response,
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> dict[str, object]:
    """Return an ephemeral preview after explicit server-processing consent."""
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if not request.preview_processing_consent:
        raise HTTPException(
            status_code=403,
            detail="Explicit consent to transient server-side preview processing is required",
        )
    context: IdentityContext | None = None
    if authorization is not None:
        context = require_authenticated_identity(authorization, request_id)
    section_field_names = None
    template_version = None
    template_id = request.template_id
    if request.saved_format_id:
        if context is None:
            context = require_authenticated_identity(authorization, request_id)
        try:
            require_format_permission(context, "use", format_id=request.saved_format_id)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        try:
            saved = create_citizen_document_format_repository().get_for_owner(
                request.saved_format_id, owner_principal_id=context.principal.principal_id
            )
        except CitizenDocumentFormatProviderConfigurationError as exc:
            raise HTTPException(status_code=503, detail="Saved formats are not configured for durable private storage") from exc
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Saved formats are temporarily unavailable") from exc
        if saved is None:
            raise HTTPException(status_code=404, detail="Saved format not found")
        template_id = saved.template_id
        template_version = saved.template_version
        section_field_names = saved.section_field_names
    workflow = CivicDraftPreviewWorkflow()
    try:
        result = workflow.preview(
            CivicDraftPreviewRequest(
                template_id=template_id,
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
                template_version=template_version,
                section_field_names=section_field_names,
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
