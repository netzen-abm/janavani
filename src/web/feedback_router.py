from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Dict, Any
import redis
import json
import os
from src.utils.feedback_validators import OfficeFeedbackSchema, ContentSanitizationEngine

router = APIRouter(prefix="/api/v1/feedback", tags=["Accountability Feedback Loop"])

# Interface credentials are deployment configuration, never source-code constants.
INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)

def _configured_interface_tokens() -> frozenset[str]:
    raw_tokens = os.getenv("JANAVANI_INTERFACE_TOKENS", "")
    return frozenset(token.strip() for token in raw_tokens.split(",") if token.strip())


def verify_client_token(token: str = Security(INTERFACE_API_KEY_HEADER)):
    if token not in _configured_interface_tokens():
        raise HTTPException(status_code=403, detail="Unauthorized interface pipeline footprint context.")
    return token


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
    )


@router.post("/submit", response_model=Dict[str, Any])
async def submit_anonymous_office_rating(
    payload: OfficeFeedbackSchema,
    token: str = Depends(verify_client_token),
    redis_db: redis.Redis = Depends(get_redis_client),
):
    """Accept anonymous citizen experience reviews from configured channel clients."""
    if not ContentSanitizationEngine.is_safe(payload.citizen_comment):
        raise HTTPException(status_code=422, detail="Commentary contains blocked phrases or unsafe character patterns.")

    sanitized_text = ContentSanitizationEngine.sanitize_commentary(payload.citizen_comment)
    office_key = f"feedback:office:{payload.office_id}"
    dept_key = f"feedback:department:{payload.department_name}"

    try:
        redis_db.hincrby(office_key, "total_reviews_count", 1)
        redis_db.hincrby(office_key, f"rating_star_{payload.service_rating}_count", 1)
        redis_db.hincrby(dept_key, "total_reviews_count", 1)

        comment_payload = {
            "rating_given": payload.service_rating,
            "comment_body": sanitized_text,
            "recorded_epoch": os.getpid(),
        }
        redis_db.lpush(f"feedback:office:{payload.office_id}:comments", json.dumps(comment_payload))
        redis_db.ltrim(f"feedback:office:{payload.office_id}:comments", 0, 49)

        return {"status": "FEEDBACK_ACCEPTED_ANONYMOUSLY", "office_targeted": payload.office_id}
    except redis.RedisError as db_fault:
        raise HTTPException(status_code=500, detail=f"Feedback memory allocation pool error: {db_fault}") from db_fault


@router.get("/summary/{office_id}", response_model=Dict[str, Any])
async def fetch_office_performance_summary(
    office_id: str,
    token: str = Depends(verify_client_token),
    redis_db: redis.Redis = Depends(get_redis_client),
):
    """Expose aggregate score dashboards only to configured internal interfaces."""
    office_key = f"feedback:office:{office_id}"

    try:
        raw_stats = redis_db.hgetall(office_key)
        raw_comments = redis_db.lrange(f"feedback:office:{office_id}:comments", 0, -1)
        parsed_comments = [json.loads(comment) for comment in raw_comments]

        return {
            "office_id": office_id,
            "aggregate_telemetry": raw_stats if raw_stats else {"total_reviews_count": 0},
            "recent_sanitized_comments": parsed_comments,
        }
    except redis.RedisError as db_fault:
        raise HTTPException(status_code=500, detail="Failed to retrieve performance ledger records.") from db_fault
