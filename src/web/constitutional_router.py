from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime, timezone

from src.core.legislative_monitor import fetch_active_bill_profile
from src.core.vernacular_headers import fetch_localized_header_map
from src.services.document_generator import MultiFormatDocumentEngine

router = APIRouter(prefix="/api/v1/constitutional", tags=["Constitutional Oversight Engine"])


class ObjectionDispatchPayload(BaseModel):
    bill_code: str
    citizen_comments: str
    requested_file_format: str = Field("PDF", description="Format choices: 'PDF' or 'DOCX'")


@router.get("/bill/{bill_code}", response_model=Dict[str, Any])
async def get_bill_compliance_report(bill_code: str):
    bill_data = fetch_active_bill_profile(bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Requested legislative bill index code not found.")
    return bill_data


@router.post("/generate-objection")
async def generate_objection(payload: ObjectionDispatchPayload):
    """Generate a citizen-editable objection document for local download/printing.

    Janavani does not dispatch this document by email. The generated file is
    returned directly to the citizen as PDF or DOCX for review, correction,
    download, and printing.
    """
    bill_data = fetch_active_bill_profile(payload.bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Target bill profile data missing.")

    evaluation = bill_data["constitutional_evaluation"]
    lang_tags = fetch_localized_header_map(bill_data["state"])

    formal_letter_body = (
        "FORMAL PETITION OF OBJECTION / MEMORANDUM OF NON-COMPLIANCE\n"
        "====================================================================\n\n"
        f"{lang_tags['salutation']}\n"
        "The Legislative Assembly Secretariat / Standing Committee Board\n"
        f"Government of {bill_data['state']}\n\n"
        f"{lang_tags['subject_prefix']} Formal Constitutional Objection Against '{bill_data['title']}'\n\n"
        "Respected Authority,\n\n"
        f"I am writing to register my formal objection to the proposed legislative draft titled '{bill_data['title']}'. "
        "An evaluation of this bill indicates significant conflicts with the Golden Triangle of the Indian Constitution "
        "(Articles 14, 19, and 21), which form the core of our fundamental human rights.\n\n"
        "CONSTITUTIONAL BREACH ANALYSIS:\n"
        f"1. ARTICLE 14 CLAUSE ASSESSMENT: {evaluation['article_14_analysis']}\n"
        f"2. ARTICLE 19 CLAUSE ASSESSMENT: {evaluation['article_19_analysis']}\n"
        f"3. ARTICLE 21 CLAUSE ASSESSMENT: {evaluation['article_21_analysis']}\n\n"
        "SUMMARY OF MATERIAL INCOMPLIANCE:\n"
        f"{evaluation['overall_constitutional_summary']}\n\n"
        "CITIZEN REASONING SUBMISSION:\n"
        f"{payload.citizen_comments}\n\n"
        f"{lang_tags['prayer_prefix']}\n"
        "The authority is requested to immediately withdraw or amend this bill to bring it into compliance with the "
        "fundamental liberties guaranteed by the Constitution of India.\n\n"
        "Submitted Sincerely,\n"
        "A Concerned Citizen of India\n"
        f"Dated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        "Generated via the Janavani Privacy-First Platform Framework."
    )

    if payload.requested_file_format.upper() == "DOCX":
        doc_stream = MultiFormatDocumentEngine.generate_docx_stream(formal_letter_body)
        return StreamingResponse(
            doc_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=objection_{payload.bill_code}.docx"},
        )

    if payload.requested_file_format.upper() != "PDF":
        raise HTTPException(status_code=400, detail="Unsupported file format. Choose PDF or DOCX.")

    pdf_stream = MultiFormatDocumentEngine.generate_pdf_stream(formal_letter_body)
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=objection_{payload.bill_code}.pdf"},
    )
