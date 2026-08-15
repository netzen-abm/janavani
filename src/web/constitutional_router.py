from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
import os
from src.core.legislative_monitor import fetch_active_bill_profile

router = APIRouter(prefix="/api/v1/constitutional", tags=["Constitutional Oversight Engine"])

class ObjectionDispatchPayload(BaseModel):
    bill_code: str
    citizen_comments: str
    target_delivery_channel: str # 'EMAIL' or 'PRINT_POST'

@router.get("/bill/{bill_code}", response_model=Dict[str, Any])
async def get_bill_compliance_report(bill_code: str):
    """Exposes constitutional reports directly to independent web and telegram client streams."""
    bill_data = fetch_active_bill_profile(bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Requested legislative bill index code not found.")
    return bill_data

@router.post("/generate-objection", response_model=Dict[str, Any])
async def generate_and_route_objection(payload: ObjectionDispatchPayload):
    """Compiles a formal constitutional objection letter based on Golden Triangle criteria."""
    bill_data = fetch_active_bill_profile(payload.bill_code)
    if not bill_data:
        raise HTTPException(status_code=404, detail="Target bill profile data missing.")
        
    evaluation = bill_data["constitutional_evaluation"]
    
    # Structure the official objection text matching traditional formal post layouts
    formal_letter_body = (
        f"FORMAL PETITION OF OBJECTION / MEMORANDUM OF NON-COMPLIANCE\n"
        f"====================================================================\n"
        f"To,\n"
        f"The Legislative Assembly Secretariat / Standing Committee Board\n"
        f"Government of {bill_data['state']}\n\n"
        f"SUBJECT: Formal Constitutional Objection Against '{bill_data['title']}'\n\n"
        f"Respected Authority,\n\n"
        f"I am writing to register my formal objection to the proposed legislative draft titled '{bill_data['title']}'. "
        f"An evaluation of this bill indicates significant conflicts with the Golden Triangle of the Indian Constitution "
        f"(Articles 14, 19, and 21), which form the core of our fundamental human rights.\n\n"
        f"CONSTITUTIONAL BREACH ANALYSIS:\n"
        f"1. ARTICLE 14 CLAUSE ASSESSMENT: {evaluation['article_14_analysis']}\n"
        f"2. ARTICLE 19 CLAUSE ASSESSMENT: {evaluation['article_19_analysis']}\n"
        f"3. ARTICLE 21 CLAUSE ASSESSMENT: {evaluation['article_21_analysis']}\n\n"
        f"SUMMARY OF MATERIAL INCOMPLIANCE:\n"
        f"{evaluation['overall_constitutional_summary']}\n\n"
        f"CITIZEN REASONING SUBMISSION:\n"
        f"\"{payload.citizen_comments}\"\n\n"
        f"PRAYER / DEMAND:\n"
        f"The authority is requested to immediately withdraw or amend this bill to bring it into compliance with the "
        f"fundamental liberties guaranteed by the Constitution of India.\n\n"
        f"Submitted Sincerely,\n"
        f"A Concerned Citizen of India\n"
        f"Dated: {datetime.utcnow().strftime('%Y-%m-%d')}\n"
        f"Generated via the Janavani Privacy-First Platform Framework."
    )

    if payload.target_delivery_channel == "PRINT_POST":
        # Returns the text block allowing the frontend to generate a printable PDF
        return {
            "delivery_mode": "PHYSICAL_POSTAL_DOWNLOAD",
            "status": "LETTER_COMPILED_FOR_PRINTING",
            "printable_text_payload": formal_letter_body
        }

    # If email delivery is requested, dispatch the letter via secure SMTP relays
    smtp_host = os.getenv("SMTP_SERVER_HOST", "smtp.janavani.internal")
    smtp_port = int(os.getenv("SMTP_SERVER_PORT", "587"))
    smtp_user = os.getenv("SMTP_SECURITY_USER", "")
    smtp_pass = os.getenv("SMTP_SECURITY_PASSWORD", "")
    
    if not smtp_user:
        return {
            "delivery_mode": "EMAIL_FALLBACK",
            "status": "SMTP_OFFLINE_DRAFT_RETURNED",
            "printable_text_payload": formal_letter_body
        }

    msg = MIMEText(formal_letter_body)
    msg["Subject"] = f"[CONSTITUTIONAL OBJECTION] Regarding {bill_data['title']}"
    msg["From"] = f"advocacy@{os.getenv('DOMAIN_NAME', 'janavani.internal')}"
    msg["To"] = "secretariat-legislation@state.gov.in" # Targeted routing point

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        return {"delivery_mode": "SECURE_EMAIL_RELAY", "status": "DISPATCHED_TO_SECRETARIAT_SUCCESSFULLY"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Mailing subsystem failed: {str(e)}")
