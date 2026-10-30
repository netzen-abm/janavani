"""Authenticated API for privacy-safe citizen-owned document format structures."""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, Field

from src.access.citizen_document_format_policy import require_format_permission
from src.documents.citizen_document_format import create_citizen_document_format, public_format_model
from src.documents.template_catalogue import get_template
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.storage.repositories.citizen_document_format_provider import (
    CitizenDocumentFormatProviderConfigurationError,
)
from src.platform.composition import create_citizen_document_format_repository

router = APIRouter(prefix="/civic/drafts/formats", tags=["Citizen Document Formats"])


class SaveCitizenFormatRequest(BaseModel):
    template_id: str = Field(min_length=1, max_length=80)
    template_version: int = Field(ge=1)
    section_field_names: list[str] = Field(min_length=1, max_length=24)
    save_confirmation: bool = False

    class Config:
        extra = "forbid"


class DeleteCitizenFormatRequest(BaseModel):
    delete_confirmation: bool = False

    class Config:
        extra = "forbid"


def _context(authorization: str | None, request_id: str | None, action: str, format_id: str | None = None) -> IdentityContext:
    context = require_authenticated_identity(authorization, request_id)
    try:
        require_format_permission(context, action, format_id=format_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return context


def _repository():
    try:
        return create_citizen_document_format_repository()
    except CitizenDocumentFormatProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail="Saved formats are not configured for durable private storage") from exc


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"


@router.get("")
def list_citizen_formats(
    response: Response,
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> dict[str, object]:
    context = _context(authorization, request_id, "list")
    _no_store(response)
    try:
        records = _repository().list_for_owner(owner_principal_id=context.principal.principal_id)
        return {"formats": [public_format_model(record) for record in records]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Saved formats are temporarily unavailable") from exc


@router.get("/{format_id}")
def get_citizen_format(
    format_id: str,
    response: Response,
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> dict[str, object]:
    context = _context(authorization, request_id, "read", format_id)
    _no_store(response)
    try:
        record = _repository().get_for_owner(format_id, owner_principal_id=context.principal.principal_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Saved formats are temporarily unavailable") from exc
    if record is None:
        raise HTTPException(status_code=404, detail="Saved format not found")
    return public_format_model(record)


@router.post("")
def save_citizen_format(
    request: SaveCitizenFormatRequest,
    response: Response,
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> dict[str, object]:
    context = _context(authorization, request_id, "save")
    _no_store(response)
    if not request.save_confirmation:
        raise HTTPException(status_code=400, detail="Explicit confirmation to save this structure is required")
    try:
        record = create_citizen_document_format(
            owner_principal_id=context.principal.principal_id,
            template_id=request.template_id,
            template_version=request.template_version,
            section_field_names=request.section_field_names,
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        saved = _repository().save(record, owner_principal_id=context.principal.principal_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Saved formats could not be stored") from exc
    return public_format_model(saved)


@router.delete("/{format_id}")
def delete_citizen_format(
    format_id: str,
    request: DeleteCitizenFormatRequest,
    response: Response,
    authorization: str | None = Header(default=None),
    request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> dict[str, object]:
    context = _context(authorization, request_id, "delete", format_id)
    _no_store(response)
    if not request.delete_confirmation:
        raise HTTPException(status_code=400, detail="Explicit confirmation to delete this saved format is required")
    try:
        deleted = _repository().delete_for_owner(format_id, owner_principal_id=context.principal.principal_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Saved formats are temporarily unavailable") from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Saved format not found")
    return {"deleted": True, "format_id": format_id}
