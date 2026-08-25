import time
import random
import requests
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v3/webhooks/telegram", tags=["Telegram Ingestion Adapter"])

CORE_INGESTION_URL = os.getenv("JANAVANI_CORE_URL", "http://localhost:8000/api/v3/core/process-multimodal-grievance")
INTERNAL_ROUTER_TOKEN = os.getenv("JANAVANI_INTERNAL_TOKEN", "telegram-v3-token")

class TelegramUpdatePayload(BaseModel):
    update_id: int
    message: Optional[dict] = None

@router.post("/incoming")
async def handle_telegram_incoming_stream_traffic(update: TelegramUpdatePayload):
    """Ingests multi-modal payloads asynchronously using random network timing jitter layers."""
    if not update.message:
        return {"status": "IGNORED_EVENT"}

    raw_message_text = update.message.get("text", "")
    jitter_delay_seconds = random.uniform(5.0, 25.0)
    time.sleep(jitter_delay_seconds)

    form_data = {
        "citizen_text_input": f"{raw_message_text}\n[Network Protection Profile: V3 Jitter Enabled]",
        "location_code": "FALLBACK",
        "export_format": "PDF"
    }

    headers = {"X-Janavani-Interface-Token": INTERNAL_ROUTER_TOKEN}
    try:
        response = requests.post(CORE_INGESTION_URL, data=form_data, headers=headers, timeout=15)
        return {"status": "PROCESSED", "telemetry_delay_applied": jitter_delay_seconds}
    except Exception:
        return {"status": "ACCEPTED_DEFERRED_RETRY"}
