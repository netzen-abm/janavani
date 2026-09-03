"""Constitutional oversight document adapter.

This route prepares objection documents for user review, printing, and
Download. JanaVani does not email or submit generated documents.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.core.legislative_monitor import fetch_active_bill_profile
from src.core.vernacular_headers import fetch_localized_header_map
from src.services.document_generator import MultiFormatDocumentEngine

router = APIRouter(
    prefix="/api/v1/constitutional",
    tags=["Constitutional Oversight Engine"],
)


class ObjectionDispatchPayload(BaseModel):
    bill_code: str
    citizen_comments: str
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


@router.post("/generate-objection")
async def generate_objection(payload: ObjectionDispatchPayload):
    """Generate an objection document for user review and download only."""
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
        raise HTTPException(
            status_code=404,
            detail="Target bill profile data missing.",
        )

    evaluation = bill_data["constitutional_evaluation"]
    lang_tags = fetch_localized_header_map(bill_data["state"])
    formal_letter_body = (
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
        "CONSTITUTIONAL BREACH ANALYSIS:\n"
        f"1. ARTICLE 14 CLAUSE ASSESSMENT: "
        f"{evaluation['article_14_analysis']}\n"
        f"2. ARTICLE 19 CLAUSE ASSESSMENT: "
        f"{evaluation['article_19_analysis']}\n"
        f"3. ARTICLE 21 CLAUSE ASSESSMENT: "
        f"{evaluation['article_21_analysis']}\n\n"
        "SUMMARY OF MATERIAL INCOMPLIANCE:\n"
        f"{evaluation['overall_constitutional_summary']}\n\n"
        "CITIZEN REASONING SUBMISSION:\n"
        f"\"{payload.citizen_comments}\"\n\n"
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

    selected_format = payload.requested_file_format.strip().upper()
    if selected_format == "DOCX":
        document_stream = MultiFormatDocumentEngine.generate_docx_stream(
            formal_letter_body
        )
        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
        filename = f"objection_{payload.bill_code}.docx"
    elif selected_format == "PDF":
        document_stream = MultiFormatDocumentEngine.generate_pdf_stream(
            formal_letter_body
        )
        media_type = "application/pdf"
        filename = f"objection_{payload.bill_code}.pdf"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use PDF or DOCX.",
        )

    return StreamingResponse(
        document_stream,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
