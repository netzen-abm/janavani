from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
import requests
import os

router = APIRouter(prefix="/api/v2/webhooks/whatsapp", tags=["WhatsApp Adapter"])

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "super-secret-verify-token-xyz")
CORE_INGESTION_URL = os.getenv("JANAVANI_CORE_URL", "http://localhost:8000/api/v2/core/process-multimodal-grievance")
INTERNAL_ROUTER_TOKEN = os.getenv("JANAVANI_INTERNAL_TOKEN", "whatsapp-v2-token")

@router.get("/incoming")
async def verify_whatsapp_webhook_registration(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: int = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """Handles the mandatory Meta cryptographic webhook challenge verification loop step."""
    if hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        from fastapi.responses import Response
        return Response(content=str(hub_challenge), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Meta verification payload token value mismatch.")

@router.post("/incoming")
async def handle_whatsapp_webhook_event(payload: dict):
    """Ingests multi-modal payload data vectors dropping from Meta business channels."""
    try:
        # Extract deep message values out from Meta's complex JSON payload schema arrays
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])[0]
        
        if not messages:
            return {"status": "NO_ACTIVE_MESSAGE_PAYLOAD"}

        user_phone = messages.get("from")
        message_type = messages.get("type")
        
        extracted_text = ""
        if message_type == "text":
            extracted_text = messages.get("text", {}).get("body", "")
        elif message_type == "voice":
            media_id = messages.get("voice", {}).get("id")
            extracted_text = f"\n[WhatsApp Voice Attachment Ref ID: {media_id}]"

        # Bundle and map parameters without logging user phone parameters or unique footprints
        form_data = {
            "citizen_text_input": f"{extracted_text}\n[Channel Trace Source: WhatsApp Business Node]",
            "location_code": "FALLBACK",
            "export_format": "PDF"
        }

        headers = {"X-Janavani-Interface-Token": INTERNAL_ROUTER_TOKEN}
        response = requests.post(CORE_INGESTION_URL, data=form_data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"status": "ACCEPTED"}
        return {"status": "BACKEND_ERROR", "code": response.status_code}
        
    except Exception:
        # Fail silently and securely with a 200 OK block to prevent Meta connection retry flooding
        return {"status": "MALFORMED_METADATA_DROPPED"}
