from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
import os
from src.core.representatives_directory import lookup_representatives
from src.storage.redis_cache_adapter import RedisCacheAdapter

router = APIRouter(prefix="/api/v1/legislative", tags=["Legislative Communication Core"])

class MailDispatchPayload(BaseModel):
    tracking_id: str
    constituency_code: str
    target_tier: str # Must be 'MP', 'MLA', or 'LSGD'

@router.get("/directory/{constituency_code}", response_model=Dict[str, Any])
async def get_constituency_directory(constituency_code: str):
    """Exposes directory data lists directly to independent frontend interface channels."""
    data = lookup_representatives(constituency_code)
    if not data:
        raise HTTPException(status_code=404, detail="Constituency tracking zone code not registered in system matrices.")
    return data

@router.post("/dispatch-email", response_model=Dict[str, Any])
async def transmit_letter_to_representative(payload: MailDispatchPayload):
    """Merges transient document details into email templates and dispatches them to officials."""

    cache_result = RedisCacheAdapter.from_env().get(f"transient_doc:{payload.tracking_id}")
    if not cache_result.ok:
        raise HTTPException(status_code=503, detail="Transient document cache is unavailable.")
    document_data = cache_result.value
    if not document_data:
        raise HTTPException(status_code=404, detail="Document tracking reference record has expired or does not exist.")

    rep_profile = lookup_representatives(payload.constituency_code)
    if not rep_profile:
        raise HTTPException(status_code=404, detail="Target constituency code map not found.")

    tier_mapping = {
        "MP": (rep_profile["mp_name"], rep_profile["mp_email"]),
        "MLA": (rep_profile["mla_name"], rep_profile["mla_email"]),
        "LSGD": (rep_profile["lsgd_body"], rep_profile["lsgd_email"])
    }

    if payload.target_tier not in tier_mapping:
        raise HTTPException(status_code=400, detail="Invalid target representative tier specified.")

    recipient_name, recipient_email = tier_mapping[payload.target_tier]
    facts_block = "\n".join([f"- {point}" for point in document_data.get("factual_points", [])])
    prayers_block = "\n".join([f"- {point}" for point in document_data.get("specific_prayers_or_requests", [])])

    email_text = (
        f"To,\n{recipient_name}\nOfficial Representative Portal Office\n\n"
        f"Subject: {document_data.get('subject_line', 'Public Grievance Submission')}\n\n"
        f"Respected Sir/Madam,\n\n"
        f"I am writing to draw your urgent attention to the following public grievance matters:\n\n"
        f"FACTUAL DISCLOSURES:\n{facts_block}\n\n"
        f"LEGAL BASIS / REASONING:\n{', '.join(document_data.get('legal_or_policy_basis', []))}\n\n"
        f"SPECIFIC PRAYERS / SOLUTIONS REQUESTED:\n{prayers_block}\n\n"
        f"Thanking you in anticipation.\n\n"
        f"Generated via Janavani Citizen Platform Portal Architecture."
    )

    smtp_host = os.getenv("SMTP_SERVER_HOST", "smtp.janavani.internal")
    smtp_port = int(os.getenv("SMTP_SERVER_PORT", "587"))
    smtp_user = os.getenv("SMTP_SECURITY_USER", "")
    smtp_pass = os.getenv("SMTP_SECURITY_PASSWORD", "")

    if not smtp_user or not smtp_pass:
        return {
            "status": "DRAFT_COMPILED_BUT_SMTP_OFFLINE",
            "target_recipient": recipient_email,
            "compiled_email_body": email_text
        }

    msg = MIMEText(email_text)
    msg["Subject"] = f"[Janavani Public Grievance] {document_data.get('subject_line')}"
    msg["From"] = f"submissions@{os.getenv('DOMAIN_NAME', 'janavani.internal')}"
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(msg["From"], [recipient_email], msg.as_string())
        return {"status": "EMAIL_DISPATCHED_SUCCESSFULLY", "dispatched_to": recipient_email}
    except Exception as email_fault:
        raise HTTPException(status_code=502, detail=f"Mail pipeline transport collapse: {type(email_fault).__name__}")
