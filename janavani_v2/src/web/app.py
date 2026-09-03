"""Compatibility API for the legacy Janavani V2 surface.

The surface remains an adapter. Document rendering is delegated to the
canonical document renderer through the compatibility facade while this
legacy route is migrated to the shared case/document capabilities.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Security, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.security.api_key import APIKeyHeader

from src.services.document_generator import MultiFormatDocumentEngine
from src.utils.validators import PrivacyPreservingTokenizer

app = FastAPI(title="Janavani V2 Master Omnichannel Gateway")
router = APIRouter(prefix="/api/v2/core", tags=["Master Platform API"])

INTERFACE_API_KEY_HEADER = APIKeyHeader(
    name="X-Janavani-Interface-Token",
    auto_error=True,
)
VALID_INTERFACE_TOKENS = frozenset(
    {
        "telegram-v2-token",
        "web-v2-token",
        "whatsapp-v2-token",
        "messenger-v2-token",
    }
)


def verify_channel_token(
    token: str = Security(INTERFACE_API_KEY_HEADER),
) -> str:
    """Validate the legacy interface credential."""
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized channel client credential request.",
        )
    return token


@router.post("/process-multimodal-grievance")
async def process_multimodal_grievance(
    citizen_text_input: Optional[str] = Form(None),
    voice_note: Optional[UploadFile] = File(None),
    evidence_photo: Optional[UploadFile] = File(None),
    evidence_video: Optional[UploadFile] = File(None),
    location_code: str = Form("FALLBACK"),
    export_format: str = Form("PDF"),
    token: str = Depends(verify_channel_token),
):
    """Create a local, printable/downloadable document artifact.

    This compatibility route does not email, submit, or transmit the
    generated document. Any action after download belongs to the user.
    """
    del evidence_photo, evidence_video, location_code, token

    resolved_issue_text = citizen_text_input or ""
    if voice_note:
        audio_bytes = await voice_note.read()
        resolved_issue_text += (
            "\n[Transcribed Audio Context Block]: "
            f"Processing {len(audio_bytes)} raw input audio bytes."
        )

    if not resolved_issue_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Grievance input parameter cannot be empty.",
        )

    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(resolved_issue_text)
    factual_text = scrubbed_data["sanitized_text"]

    formal_letter_body = (
        "FORMAL PUBLIC GRIEVANCE PETITION / MEMORANDUM OF ACCOUNTABILITY\n"
        "====================================================================\n"
        "AUTHORITY ANCHOR: Derived under the Preamble "
        "('WE, THE PEOPLE OF INDIA') read with Article 51A "
        "(Fundamental Duties) of the Constitution of India.\n\n"
        "To,\n"
        "The Competent Administrative Officer / Public Authority\n\n"
        "SUBJECT: Urgent Rectification and Accountability Demand\n\n"
        "CONSTITUTIONAL INVOCATION CONTEXT:\n"
        "This petition is prepared for user review and correction.\n\n"
        "FACTUAL DISCLOSURES:\n"
        f"- {factual_text}\n\n"
        "PRAYER / REMEDIAL REQUEST:\n"
        "- Immediate consideration and appropriate administrative action.\n\n"
        "Submitted Sincerely,\n"
        "Citizen\n"
        f"Dated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
        "--------------------------------------------------------------------\n"
        "USER DELIVERY NOTICE:\n"
        "This file is generated for user review, printing, and download. "
        "JanaVani does not email or submit this document."
    )

    selected_format = export_format.strip().upper()
    if selected_format == "DOCX":
        file_stream = MultiFormatDocumentEngine.generate_docx_stream(
            formal_letter_body
        )
        media_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
        filename = f"petition_{uuid.uuid4().hex[:8]}.docx"
    elif selected_format == "PDF":
        file_stream = MultiFormatDocumentEngine.generate_pdf_stream(
            formal_letter_body
        )
        media_type = "application/pdf"
        filename = f"petition_{uuid.uuid4().hex[:8]}.pdf"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported export format. Use PDF or DOCX.",
        )

    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


app.include_router(router)

# Legacy channel adapters remain independently mounted.
from src.adapters.telegram_webhook import router as telegram_channel_router
from src.adapters.whatsapp_webhook import router as whatsapp_channel_router
from src.web.volunteer_router import router as volunteer_network_router

app.include_router(telegram_channel_router)
app.include_router(whatsapp_channel_router)
app.include_router(volunteer_network_router)
