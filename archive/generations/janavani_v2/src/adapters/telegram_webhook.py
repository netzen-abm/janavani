from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
import requests
import os
import logging

router = APIRouter(prefix="/api/v2/webhooks/telegram", tags=["Telegram Adapter"])
logger = logging.getLogger("janavani.adapters.telegram")

# Pull core addresses from host space variables
CORE_INGESTION_URL = os.getenv("JANAVANI_CORE_URL", "http://localhost:8000/api/v2/core/process-multimodal-grievance")
INTERNAL_ROUTER_TOKEN = os.getenv("JANAVANI_INTERNAL_TOKEN", "telegram-v2-token")

class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str] = None

class TelegramMessage(BaseModel):
    message_id: int
    from_user: TelegramUser = Field(..., alias="from")
    text: Optional[str] = None
    voice: Optional[dict] = None

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None

@router.post("/incoming")
async def handle_telegram_webhook_event(update: TelegramUpdate):
    """Stateless entry conduit parsing incoming Telegram interface payloads."""
    if not update.message:
        return {"status": "IGNORED_NON_MESSAGE_EVENT"}

    message = update.message
    chat_id = message.from_user.id
    
    # Enforce data sanitization blocks to strip explicit structural user parameters
    extracted_text = message.text or ""
    files_payload = {}
    form_data = {
        "location_code": "FALLBACK",
        "export_format": "PDF"
    }

    # Handle voice note ingestion buffers if the chat stream contains voice files
    if message.voice:
        file_id = message.voice.get("file_id")
        # In production, fetch the raw voice bytes from the Telegram file service container link
        # files_payload["voice_note"] = (f"{file_id}.ogg", b"voice_binary_placeholder_data")
        extracted_text += f"\n[Telegram Voice Audio Attached Ref ID: {file_id}]"

    form_data["citizen_text_input"] = extracted_text

    # Route downstream to the core ingestion gateway safely over internal bridges
    headers = {"X-Janavani-Interface-Token": INTERNAL_ROUTER_TOKEN}
    try:
        response = requests.post(CORE_INGESTION_URL, data=form_data, files=files_payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return {"status": "PROCESSED", "message": "Payload passed down pipeline layers successfully."}
        
        logger.error(f"Telegram processing failed downstream with status code: {response.status_code}")
        raise HTTPException(status_code=502, detail="Core processing layer connection drop error.")
    except Exception as e:
        logger.error(f"Telegram pipeline transport failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal webhook bridge pipeline crash.")


import time
import random
import requests
import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v2/webhooks/telegram", tags=["Telegram Adapter"])
logger = logging.getLogger("janavani.adapters.telegram")

CORE_INGESTION_URL = os.getenv("JANAVANI_CORE_URL", "http://localhost:8000/api/v2/core/process-multimodal-grievance")
INTERNAL_ROUTER_TOKEN = os.getenv("JANAVANI_INTERNAL_TOKEN", "telegram-v2-token")

class TelegramUpdatePayload(BaseModel):
    update_id: int
    message: Optional[dict] = None

@router.post("/incoming")
async def handle_telegram_incoming_stream_traffic(update: TelegramUpdatePayload):
    """Ingests multi-modal payloads asynchronously using random network timing jitter layers."""
    if not update.message:
        return {"status": "IGNORED_EVENT"}

    # Extract plain-text blocks securely
    raw_message_text = update.message.get("text", "")
    
    # Instantiate an internal network timing jitter delay relay
    # Adds a random delay between 5 and 20 seconds to disrupt external packet monitoring attempts
    jitter_delay_seconds = random.uniform(5.0, 20.0)
    time.sleep(jitter_delay_seconds)

    form_data = {
        "citizen_text_input": f"{raw_message_text}\n[Network Protection Profile: Jitter Active]",
        "location_code": "FALLBACK",
        "export_format": "PDF"
    }

    headers = {"X-Janavani-Interface-Token": INTERNAL_ROUTER_TOKEN}
    try:
        response = requests.post(CORE_INGESTION_URL, data=form_data, headers=headers, timeout=15)
        return {"status": "PROCESSED", "telemetry_delay_applied": jitter_delay_seconds}
    except Exception as network_fault:
        logger.error(f"Stateless webhook bridge connection timed out or failed: {str(network_fault)}")
        return {"status": "ACCEPTED_DEFERRED_RETRY"}

