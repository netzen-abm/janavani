"""Constitutional oversight access-surface adapter.

This route prepares objection documents from an owned canonical Case. JanaVani
does not email or submit generated documents.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.capabilities.constitutional_objection import ConstitutionalObjectionCapability
from src.core.legislative_monitor import fetch_active_bill_profile
from src.documents.document_contract import DocumentFormat
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.platform.composition import (
    create_authority_repository,
    create_case_repository,
    create_constitutional_objection_capability,
)

router = APIRouter(
    prefix="/api/v1/constitutional",
    tags=["Constitutional Oversight Engine"],
)

_REPOSITORY = create_case_repository()
_AUTHORITY_REPOSITORY = create_authority_repository()
_CAPABILITY: ConstitutionalObjectionCapability = create_constitutional_objection_capability(
    case_repository=_REPOSITORY,
    authority_repository=_AUTHORITY_REPOSITORY,
    bill_profile_loader=fetch_active_bill_profile,
)


class ObjectionDispatchPayload(BaseModel):
    case_id: str = Field(min_length=1, description="Canonical objection Case owned by the caller.")
    bill_code: str
    citizen_comments: str
    target_delivery_channel: str = Field("DOWNLOAD", description="Only DOWNLOAD is supported by JanaVani.")
    requested_file_format: str = Field("PDF", description="Format choices: PDF or DOCX.")


@router.get("/bill/{bill_code}", response_model=Dict[str, Any])
async def get_bill_compliance_report(bill_code: str):
    """Return the available legislative compliance profile."""
    bill_data = fetch_active_bill_profile(bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Requested legislative bill index code not found.")
    return bill_data


@router.post("/generate-objection")
async def generate_objection(
    payload: ObjectionDispatchPayload,
    context: IdentityContext = Depends(require_authenticated_identity),
):
    """Generate an objection artifact through the canonical Case boundary."""
    if payload.target_delivery_channel.strip().upper() != "DOWNLOAD":
        raise HTTPException(
            status_code=400,
            detail=(
                "JanaVani does not email or submit generated documents. "
                "Use DOWNLOAD and take any later action independently."
            ),
        )

    selected_format = payload.requested_file_format.strip().upper()
    if selected_format not in {"DOCX", "PDF"}:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF or DOCX.")

    try:
        artifact = _CAPABILITY.generate_reviewable_artifact(
            payload.case_id,
            identity=context,
            bill_code=payload.bill_code,
            citizen_comments=payload.citizen_comments,
            document_format=DocumentFormat(selected_format.lower()),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    filename = f"objection_{payload.bill_code}.{selected_format.lower()}"
    media_type = (
        "application/pdf"
        if selected_format == "PDF"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    stream = _CAPABILITY.open_artifact(artifact)
    return StreamingResponse(
        stream,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-JanaVani-Case-Id": payload.case_id,
            "X-JanaVani-Artifact-SHA256": artifact.reference.content_sha256,
        },
    )
