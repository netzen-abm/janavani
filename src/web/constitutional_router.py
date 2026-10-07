"""Constitutional oversight access-surface adapter.

This route prepares objection documents from an owned canonical Case. JanaVani
does not email or submit generated documents.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from src.capabilities.constitutional_objection import ConstitutionalObjectionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.core.legislative_monitor import fetch_active_bill_profile
from src.documents.document_contract import DocumentFormat
from src.documents.artifact_service import render_artifact_payload
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.platform.composition import create_constitutional_objection_capability, create_provider_composition
from src.platform.composition_repositories import create_document_review_repository_for_platform
from src.platform.runtime import AUTHORITY_REPOSITORY, CASE_REPOSITORY

router = APIRouter(prefix="/api/v1/constitutional", tags=["Constitutional Oversight Engine"])

_REPOSITORY = CASE_REPOSITORY
_AUTHORITY_REPOSITORY = AUTHORITY_REPOSITORY
_DOCUMENT_REVIEW = DocumentReviewCapability(
    create_document_review_repository_for_platform(provider_composition=create_provider_composition()),
    case_capability=CivicCaseCapability(_REPOSITORY),
)
_CAPABILITY: ConstitutionalObjectionCapability = create_constitutional_objection_capability(
    case_repository=_REPOSITORY,
    authority_repository=_AUTHORITY_REPOSITORY,
    bill_profile_loader=fetch_active_bill_profile,
    document_review_capability=_DOCUMENT_REVIEW,
)


class ObjectionDispatchPayload(BaseModel):
    case_id: str = Field(min_length=1, description="Canonical objection Case owned by the caller.")
    bill_code: str
    citizen_comments: str
    target_delivery_channel: str = Field("DOWNLOAD", description="Only DOWNLOAD is supported by JanaVani.")
    requested_file_format: str = Field("PDF", description="Format choices: PDF or DOCX.")


@router.get("/bill/{bill_code}", response_model=Dict[str, Any])
async def get_bill_compliance_report(bill_code: str):
    bill_data = fetch_active_bill_profile(bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Requested legislative bill index code not found.")
    return bill_data


@router.post("/generate-objection")
async def generate_objection(payload: ObjectionDispatchPayload,
                             context: IdentityContext = Depends(require_authenticated_identity)):
    if payload.target_delivery_channel.strip().upper() != "DOWNLOAD":
        raise HTTPException(status_code=400, detail=(
            "JanaVani does not email or submit generated documents. "
            "Use DOWNLOAD and take any later action independently."
        ))

    selected_format = payload.requested_file_format.strip().upper()
    if selected_format not in {"DOCX", "PDF"}:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF or DOCX.")

    try:
        result = _CAPABILITY.build_document(
            payload.case_id,
            identity=context,
            bill_code=payload.bill_code,
            citizen_comments=payload.citizen_comments,
        )
        rendered = render_artifact_payload(result.draft, DocumentFormat(selected_format.lower()))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return Response(
        content=rendered.content,
        media_type=rendered.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="objection_{payload.bill_code}.{selected_format.lower()}"',
            "X-JanaVani-Case-Id": payload.case_id,
            "X-JanaVani-Artifact-SHA256": rendered.content_sha256,
            "Cache-Control": "no-store, private",
            "X-Janavani-Delivery": "citizen-download-only",
        },
    )
