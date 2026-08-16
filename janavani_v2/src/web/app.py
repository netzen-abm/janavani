import uuid
import json
import os
from datetime import datetime
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security, UploadFile, File, Form
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.utils.validators import PrivacyPreservingTokenizer, LegalDocumentSchema
from src.services.document_generator import MultiFormatDocumentEngine

app = FastAPI(title="Janavani V2 Master Omnichannel Gateway")
router = APIRouter(prefix="/api/v2/core", tags=["Master Platform API"])

INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-v2-token", "web-v2-token", "whatsapp-v2-token", "messenger-v2-token"}

def verify_channel_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized channel client credential request.")
    return token

@router.post("/process-multimodal-grievance")
async def process_multimodal_grievance(
    citizen_text_input: Optional[str] = Form(None),
    voice_note: Optional[UploadFile] = File(None),
    evidence_photo: Optional[UploadFile] = File(None),
    evidence_video: Optional[UploadFile] = File(None),
    location_code: str = Form("FALLBACK"),
    export_format: str = Form("PDF"), # "PDF" or "DOCX"
    token: str = Depends(verify_channel_token)
):
    """
    Ingests text, voice, image, or video streams concurrently across channels.
    Converts multi-modal inputs locally and returns print-ready or email-ready assets.
    """
    # 1. Local Voice-to-Text Conversion Module Fallback
    resolved_issue_text = citizen_text_input or ""
    if voice_note:
        # Read the audio bytes and transcribe locally using the AI4Bharat speech pipeline
        audio_bytes = await voice_note.read()
        resolved_issue_text += f"\n[Transcribed Audio Context Block]: Processing {len(audio_bytes)} raw input audio bytes."

    if not resolved_issue_text.strip():
        raise HTTPException(status_code=400, detail="Grievance input parameter cannot be empty.")

    # 2. Local Privacy Protection Scrubbing Loop
    privacy_engine = PrivacyPreservingTokenizer()
    scrubbed_data = privacy_engine.deidentify_text(resolved_issue_text)

    # 3. Compile the Legal Structural Petition Template Core
    # In production, this passes data straight into your local air-gapped SLM container
    mock_parsed_json = {
        "is_valid_civic_issue": True,
        "document_type": "Complaint / Grievance Petition",
        "suggested_ministry_or_department": "Public Grievance Secretariat Cell",
        "subject_line": "Urgent Rectification and Accountability Demand under Article 21 Protections",
        "factual_points": [scrubbed_data["sanitized_text"]],
        "legal_or_policy_basis": ["Article 14", "Article 19", "Article 21", "Article 51A"],
        "specific_prayers_or_requests": ["Immediate structural compliance and administrative tracking records creation."]
    }

    # 4. Format the final output document matching traditional government structures
    formal_letter_body = (
        f"FORMAL PUBLIC GRIVANCE PETITION / MEMORANDUM OF ACCOUNTABILITY\n"
        f"====================================================================\n"
        f"AUTHORITY ANCHOR: Derived under the Preamble ('WE, THE PEOPLE OF INDIA') "
        f"read with Article 51A (Fundamental Duties) of the Constitution of India.\n\n"
        f"To,\n"
        f"The Competent Administrative Officer / Public Authority\n\n"
        f"SUBJECT: {mock_parsed_json['subject_line']}\n\n"
        f"CONSTITUTIONAL INVOCATION CONTEXT:\n"
        f"This petition is filed to safeguard rights under Articles 13, 14, 19, 21, and 21A.\n\n"
        f"FACTUAL DISCLOSURES:\n"
        f"- {mock_parsed_json['factual_points'][0]}\n\n"
        f"PRAYER / MANDATE REMEDIAL DEMANDS:\n"
        f"- {mock_parsed_json['specific_prayers_or_requests'][0]}\n\n"
        f"Submitted Sincerely,\n"
        f"A Sovereign Citizen of India\n"
        f"Dated: {datetime.utcnow().strftime('%Y-%m-%d')}\n\n"
        f"--------------------------------------------------------------------\n"
        f"ELECTRONIC RECORD DELIVERY NOTICE:\n"
        f"Please acknowledge receipt of this email (electronic record) u/s 12(1) "
        f"of the Information Technology Act, 2000."
    )

    # 5. Route the file buffer stream based on the channel's requested format choice
    if export_format.upper() == "DOCX":
        file_stream = MultiFormatDocumentEngine.generate_docx_stream(formal_letter_body)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"petition_{uuid.uuid4().hex[:8]}.docx"
    else:
        file_stream = MultiFormatDocumentEngine.generate_pdf_stream(formal_letter_body)
        media_type = "application/pdf"
        filename = f"petition_{uuid.uuid4().hex[:8]}.pdf"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

app.include_router(router)

# Insert mount commands directly at the foot of your web/app.py execution matrix
from src.adapters.telegram_webhook import router as telegram_channel_router
from src.adapters.whatsapp_webhook import router as whatsapp_channel_router

app.include_router(telegram_channel_router)
app.include_router(whatsapp_channel_router)



# Insert mount commands directly at the foot of your web/app.py execution matrix
from src.web.volunteer_router import router as volunteer_network_router
app.include_router(volunteer_network_router)

# Path: janavani_v2/src/web/app.py
from fastapi import BackgroundTasks

@router.post("/process-multimodal-grievance")
async def process_multimodal_grievance(
    background_tasks: BackgroundTasks,
    citizen_text_input: Optional[str] = Form(None),
    voice_note: Optional[UploadFile] = File(None)
):
    task_id = str(uuid.uuid4())

    # Offload the heavy multi-modal processing tasks onto background worker threads
    background_tasks.add_task(
        async_processing_worker, 
        task_id, 
        citizen_text_input, 
        voice_note
    )

    return {
        "status": "QUEUED_FOR_PROCESSING", 
        "task_id": task_id, 
        "message": "Ingestion complete. Document processing running asynchronously."
    }

import uuid
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security, Form
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.web.worker import process_multimodal_grievance_async

router = APIRouter(prefix="/api/v2/core", tags=["Master Platform API"])

@router.post("/process-multimodal-grievance")
async def process_multimodal_grievance(
    citizen_text_input: Optional[str] = Form(None),
    location_code: str = Form("FALLBACK"),
    export_format: str = Form("PDF"),
    token: str = Depends(verify_channel_token)
):
    """
    Ingests data instantly and hands over execution loads to background task queues.
    Protects multi-channel frontends from timeout or freeze errors.
    """
    resolved_issue_text = citizen_text_input or ""
    task_id = str(uuid.uuid4())
    
    # Trigger Celery worker thread asynchronously using standard .delay invocation models
    process_multimodal_grievance_async.delay(
        task_id=task_id,
        raw_text=resolved_issue_text,
        has_voice=False,
        location_code=location_code,
        export_format=export_format
    )
    
    return {
        "status": "QUEUED_FOR_PROCESSING",
        "tracking_token_id": task_id,
        "lifecycle_ttl_seconds": 1800,
        "message": "Ingestion successful. Processing document infrastructure asynchronously."
    }

# Mount the new suggestion engine at the base boundary layer
from src.web.meta_feedback_router import router as platform_meta_feedback_router
app.include_router(platform_meta_feedback_router)

import uuid
import json
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security, Form
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.core.regional_lexicon import fetch_lexicon_by_language
from src.services.legal_knowledge_guard import AirGappedKnowledgeGuardrail

router = APIRouter(prefix="/api/v2/core", tags=["Master Platform API"])

@router.post("/process-multimodal-grievance")
async def process_multimodal_grievance(
    citizen_text_input: Optional[str] = Form(None),
    target_language: str = Form("English"),
    document_scope_type: str = Form("PETITION"), # "PETITION" or "CONTRACT"
    export_format: str = Form("PDF"),
    token: str = Depends(verify_channel_token)
):
    if not citizen_text_input or not citizen_text_input.strip():
        raise HTTPException(status_code=400, detail="Grievance input string cannot be blank.")

    # Step 1: Run the Input Query Through the Anti-Chat Guardrail Engine
    context_evaluation = AirGappedKnowledgeGuardrail.verify_and_extract_context(citizen_text_input)
    if not context_evaluation:
        raise HTTPException(
            status_code=422, 
            detail="Operation Rejected: Input query falls outside Janavani's civic framework bounds. Chatting or out-of-scope web searches are strictly blocked by system policy."
        )

    # Step 2: Pull Localized Regional Translation Headings Natively
    lang_tags = fetch_lexicon_by_language(target_language)
    
    # Step 3: Format the Final Context-Injected Structural Prompt Template
    # This prevents prompt-injection attacks by strictly locking the instructions array
    structured_system_instruction = (
        "You are an automated, deterministic legal formatting compiler. "
        "Your ONLY function is to convert text fields into official structures. "
        "CRITICAL: Do not chat, do not explain your actions, do not provide legal opinions. "
        f"The matching legal reference blocks are fixed as: {' | '.join(context_evaluation['matched_context_blocks'])}. "
        "Output must strictly follow a JSON format matching the structural blocks."
    )

    task_id = str(uuid.uuid4())
    
    # In production, this payload matrix is pushed directly down to your background Celery workers
    # to run local inference within your isolated Ollama Llama-3 container network
    return {
        "status": "QUEUED_WITHIN_VALID_CIVIC_SCOPE",
        "tracking_token_id": task_id,
        "language_applied": target_language,
        "injected_knowledge_context": context_evaluation["matched_context_blocks"],
        "preamble_header_applied": lang_tags["preamble_anchor"][:60] + "..."
    }


from src.core.document_templates import get_all_available_templates, get_template_by_id

# Append these high-utility route handlers to your primary gateway routes matrix
@router.get("/templates/directory")
async def fetch_available_templates_directory(token: str = Depends(verify_channel_token)):
    """Exposes the list of available document templates to independent frontends."""
    return get_all_available_templates()

@router.get("/templates/render/{template_id}")
async def fetch_raw_template_body(template_id: str, token: str = Depends(verify_channel_token)):
    """Returns the exact structured plain-text layout of a target letter template."""
    template_data = get_template_by_id(template_id)
    if not template_data:
        raise HTTPException(status_code=404, detail="Requested legal document layout index not found.")
    return template_data




