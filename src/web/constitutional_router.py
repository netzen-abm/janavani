"""Constitutional oversight HTTP adapter.

Constitutional objections use the canonical Case → Authority → Document
artifact path. Generation is review/download only; submission is separate.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.core.civic_case import CaseType
from src.core.legislative_monitor import fetch_active_bill_profile
from src.core.vernacular_headers import fetch_localized_header_map
from src.documents.document_contract import DocumentFormat
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.platform.composition import (
    create_authority_repository,
    create_case_capability,
    create_case_repository,
    create_civic_action_capability,
)
from src.storage.artifact_blob_factory import create_artifact_blob_store

router = APIRouter(
    prefix="/api/v1/constitutional",
    tags=["Constitutional Oversight Engine"],
)

_REPOSITORY = create_case_repository()
_CAPABILITY = create_case_capability(_REPOSITORY)
_AUTHORITY_REPOSITORY = create_authority_repository()
_ARTIFACT_BLOB_STORE = create_artifact_blob_store()
_CIVIC_ACTION_CAPABILITY = create_civic_action_capability(
    case_repository=_REPOSITORY,
    authority_repository=_AUTHORITY_REPOSITORY,
)
# The action capability receives the same blob store used by this adapter so
# the returned artifact can be opened without introducing another storage path.
_CIVIC_ACTION_CAPABILITY._blob_store = _ARTIFACT_BLOB_STORE


class ObjectionDispatchPayload(BaseModel):
    bill_code: str
    citizen_comments: str = Field(min_length=1)
    authority_id: str = Field(min_length=1)
    target_delivery_channel: str = Field(
        "DOWNLOAD",
        description="Only DOWNLOAD is supported by JanaVani.",
    )
    requested_file_format: str = Field(
        "PDF",
        description="Format choices: PDF or DOCX.",
    )


@router.get("/bill/{bill_code}", response_model=Dict[str, Any])
async def get_bill_compliance_report(bill_code: str):
    """Return the available legislative compliance profile."""
    bill_data = fetch_active_bill_profile(bill_code)
    if not bill_data:
        raise HTTPException(
            status_code=404,
            detail="Requested legislative bill index code not found.",
        )
    return bill_data


def _build_objection_body(bill_data: dict[str, Any], citizen_comments: str) -> str:
    """Convert the legislative profile into citizen-reviewable document prose.

    The evaluation is retained as source analysis, not promoted here into a
    verified legal determination.
    """
    evaluation = bill_data["constitutional_evaluation"]
    lang_tags = fetch_localized_header_map(bill_data["state"])
    return (
        "FORMAL PETITION OF OBJECTION / MEMORANDUM OF NON-COMPLIANCE\n"
        "====================================================================\n\n"
        f"{lang_tags['salutation']}\n"
        "The Legislative Assembly Secretariat / Standing Committee Board\n"
        f"Government of {bill_data['state']}\n\n"
        f"{lang_tags['subject_prefix']} Formal Constitutional Objection Against "
        f"'{bill_data['title']}'\n\n"
        "Respected Authority,\n\n"
        f"I am writing to register my formal objection to the proposed "
        f"legislative draft titled '{bill_data['title']}'.\n\n"
        "LEGISLATIVE PROFILE ANALYSIS (SOURCE DATA; NOT AN INDEPENDENT LEGAL DETERMINATION):\n"
        f"1. ARTICLE 14 CLAUSE ASSESSMENT: {evaluation['article_14_analysis']}\n"
        f"2. ARTICLE 19 CLAUSE ASSESSMENT: {evaluation['article_19_analysis']}\n"
        f"3. ARTICLE 21 CLAUSE ASSESSMENT: {evaluation['article_21_analysis']}\n\n"
        "SUMMARY OF SOURCE ANALYSIS:\n"
        f"{evaluation['overall_constitutional_summary']}\n\n"
        "CITIZEN REASONING SUBMISSION:\n"
        f"\"{citizen_comments}\"\n\n"
        f"{lang_tags['prayer_prefix']}\n"
        "The authority is requested to consider the stated objection and "
        "take appropriate action.\n\n"
        "Submitted Sincerely,\n"
        "A Concerned Citizen of India\n"
        f"Dated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
        "USER DELIVERY NOTICE:\n"
        "This file is generated for user review, printing, and download. "
        "JanaVani does not email or submit this document."
    )


@router.post("/generate-objection")
async def generate_objection(
    payload: ObjectionDispatchPayload,
    context: IdentityContext = Depends(require_authenticated_identity),
):
    """Create an owned canonical objection Case and a reviewable artifact."""
    if payload.target_delivery_channel.strip().upper() != "DOWNLOAD":
        raise HTTPException(
            status_code=400,
            detail=(
                "JanaVani does not email or submit generated documents. "
                "Use DOWNLOAD and take any later action independently."
            ),
        )

    bill_data = fetch_active_bill_profile(payload.bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Target bill profile data missing.")

    selected_format = payload.requested_file_format.strip().lower()
    try:
        document_format = DocumentFormat(selected_format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF or DOCX.") from exc

    case_result = _CAPABILITY.create(
        request=__import__("src.capabilities.civic_case", fromlist=["CivicCaseCreateRequest"]).CivicCaseCreateRequest(
            case_type=CaseType.OBJECTION,
            subject=f"Formal Constitutional Objection Against '{bill_data['title']}'",
            narrative=_build_objection_body(bill_data, payload.citizen_comments),
            jurisdiction={"state": bill_data["state"], "region": bill_data.get("region", "")},
            related_office_id=payload.authority_id,
            claims=[
                {
                    "claim_type": "legislative_source",
                    "bill_code": payload.bill_code,
                    "title": bill_data["title"],
                    "status": bill_data.get("status"),
                    "source": "src.core.legislative_monitor.LIVE_LEGISLATIVE_BILL_REGISTRY",
                },
                {
                    "claim_type": "constitutional_evaluation",
                    "provenance": "legislative_profile_analysis",
                    "verified": False,
                    "evaluation": bill_data["constitutional_evaluation"],
                },
            ],
        ),
        identity=context,
        source_channel="webapp",
    )

    try:
        artifact = _CIVIC_ACTION_CAPABILITY.generate_reviewable_artifact(
            case_result.case.case_id,
            identity=context,
            document_format=document_format,
            blob_store=_ARTIFACT_BLOB_STORE,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    stored = _ARTIFACT_BLOB_STORE.open(artifact.reference.storage_ref)
    extension = document_format.value
    media_type = (
        "application/pdf"
        if document_format is DocumentFormat.PDF
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    filename = f"objection_{payload.bill_code}_{artifact.reference.artifact_id.split(':')[0]}.{extension}"
    return StreamingResponse(
        stored,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
