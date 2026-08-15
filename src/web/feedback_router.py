from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Dict, Any, List
import redis
import json
import os
from src.utils.feedback_validators import OfficeFeedbackSchema, ContentSanitizationEngine

router = APIRouter(prefix="/api/v1/feedback", tags=["Accountability Feedback Loop"])

# Protect data entry endpoints using unified platform authorization tokens
INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)
VALID_INTERFACE_TOKENS = {"telegram-mvp-token-xyz", "web-mvp-token-abc", "android-client-token-123"}

def verify_client_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in VALID_INTERFACE_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized interface pipeline footprint context.")
    return token

def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )

@router.post("/submit", response_model=Dict[str, Any])
async def submit_anonymous_office_rating(
    payload: OfficeFeedbackSchema,
    token: str = Depends(verify_client_token),
    redis_db: redis.Redis = Depends(get_redis_client)
):
    """Accepts anonymous citizen experience reviews from any independent channel client interface."""
    
    # Step 1: Enforce Safety Filter Layers Locally
    if not ContentSanitizationEngine.is_safe(payload.citizen_comment):
        raise HTTPException(status_code=422, detail="Commentary contains blocked phrases or unsafe character patterns.")
        
    sanitized_text = ContentSanitizationEngine.sanitize_commentary(payload.citizen_comment)
    
    # Step 2: Atomic Tracking Vector Calculations (Aggregates Only)
    office_key = f"feedback:office:{payload.office_id}"
    dept_key = f"feedback:department:{payload.department_name}"
    
    try:
        # Increment rating metrics counters atomically in Redis memory
        redis_db.hincrby(office_key, "total_reviews_count", 1)
        redis_db.hincrby(office_key, f"rating_star_{payload.service_rating}_count", 1)
        redis_db.hincrby(dept_key, "total_reviews_count", 1)
        
        # Save a historical log of the comment completely detached from any user identifiers
        comment_payload = {
            "rating_given": payload.service_rating,
            "comment_body": sanitized_text,
            "recorded_epoch": os.getpid() # Abstract environment timestamp index to keep logs anonymous
        }
        redis_db.lpush(f"feedback:office:{payload.office_id}:comments", json.dumps(comment_payload))
        # Keep list size bounded at 50 records to save memory space
        redis_db.ltrim(f"feedback:office:{payload.office_id}:comments", 0, 49)
        
        return {"status": "FEEDBACK_ACCEPTED_ANONYMOUSLY", "office_targeted": payload.office_id}
        
    except redis.RedisError as db_fault:
        raise HTTPException(status_code=500, detail=f"Feedback memory allocation pool error: {str(db_fault)}")

@router.get("/summary/{office_id}", response_model=Dict[str, Any])
async def fetch_office_performance_summary(office_id: str, redis_db: redis.Redis = Depends(get_redis_client)):
    """Exposes aggregate score dashboards publicly to both Web and Telegram interfaces."""
    office_key = f"feedback:office:{office_id}"
    
    try:
        raw_stats = redis_db.hgetall(office_key)
        raw_comments = redis_db.lrange(f"feedback:office:{office_id}:comments", 0, -1)
        
        parsed_comments = [json.loads(c) for c in raw_comments]
        
        return {
            "office_id": office_id,
            "aggregate_telemetry": raw_stats if raw_stats else {"total_reviews_count": 0},
            "recent_sanitized_comments": parsed_comments
        }
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Failed to retrieve performance ledger records.")
