import uuid
import json
import os
from datetime import datetime
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Security, Form
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Any, Optional
import redis

app = FastAPI(title="Janavani V3 Sovereign Governance Operating System")
router = APIRouter(prefix="/api/v3/core")

INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-v3-token", "web-v3-token", "whatsapp-v3-token", "messenger-v3-token"}

def verify_channel_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized interface client token.")
    return token

def get_redis_client():
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

class ProcessIssueRequest(BaseModel):
    citizen_raw_input: str

class HardenedFeedbackSchema(BaseModel):
    office_id: str
    department_name: str
    service_rating: int
    citizen_comment: str
    zk_action_token_id: str

@router.post("/process-multimodal-grievance")
async def process_grievance_v3(payload: ProcessIssueRequest, token: str = Depends(verify_channel_token), redis_db: redis.Redis = Depends(get_redis_client)):
    """Ingests text prompts, validates civic scope rules, and prepares background tasks [source 1]."""
    text = payload.citizen_raw_input.lower().strip()
    
    # V2/V3 ANTI-CHAT GUARDRAILS ENFORCEMENT
    allowed_keywords = ["bill", "act", "amendment", "grievance", "complaint", "land", "gata", "rti", "police", "officer"]
    if not any(kw in text for kw in allowed_keywords):
        raise HTTPException(
            status_code=422, 
            detail="Operation Rejected: Input query falls outside Janavani's civic framework bounds. Chatting or out-of-scope web searches are strictly blocked by system policy."
        )

    task_id = str(uuid.uuid4())
    # Cache initial state token inside volatile in-memory layers [source 1]
    redis_db.hset(f"transient_doc:results:{task_id}", "status", "QUEUED")
    redis_db.expire(f"transient_doc:results:{task_id}", 1800)

    return {"status": "QUEUED_WITHIN_VALID_CIVIC_SCOPE", "tracking_token_id": task_id}

@router.post("/feedback/submit")
async def submit_authenticated_rating(payload: HardenedFeedbackSchema, redis_db: redis.Redis = Depends(get_redis_client)):
    """V3 Single-Use Token Accountability Review Gateway (Prevents review manipulation)."""
    token_tracking_key = f"transient_doc:results:{payload.zk_action_token_id}"
    
    if not redis_db.exists(token_tracking_key):
        raise HTTPException(status_code=403, detail="Review rejected: Invalid or unverified platform action token.")
        
    # Enforce one-time verification policy: burn token instantly
    redis_db.delete(token_tracking_key)
    
    office_score_key = f"feedback:office:{payload.office_id}"
    redis_db.hincrby(office_score_key, "total_reviews_count", 1)
    redis_db.hincrby(office_score_key, f"rating_star_{payload.service_rating}_count", 1)
    
    return {"status": "AUTHENTICATED_FEEDBACK_ACCEPTED"}

# Mount external structural routes matrices safely
from src.web.land_router import router as land_revenue_router
app.include_router(router)
app.include_router(land_revenue_router)
