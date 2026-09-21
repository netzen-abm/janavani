from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import redis
import json
import os

router = APIRouter(prefix="/api/v2/meta-feedback", tags=["Platform Meta Feedback Loop"])

class PlatformSuggestionSchema(BaseModel):
    feature_scope_tag: str = Field(..., description="Target system module, e.g., 'UI', 'AI-Drafting', 'SOS-Mesh'")
    user_suggestion_body: str = Field(..., description="User insights regarding system behavior or upgrades.")

def get_redis_client():
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

@router.post("/submit", response_model=Dict[str, Any])
async def submit_platform_improvement_insight(payload: PlatformSuggestionSchema, redis_db: redis.Redis = Depends(get_redis_client)):
    """Logs anonymous citizen optimization insights to help improve the platform's core codebases."""
    
    cleaned_suggestion = payload.user_suggestion_body.strip()
    if len(cleaned_suggestion) > 500:
        cleaned_suggestion = cleaned_suggestion[:497] + "..."

    suggestion_block = {
        "module": payload.feature_scope_tag.upper(),
        "suggestion": cleaned_suggestion,
        "epoch_recorded": os.getpid()
    }

    try:
        # Push suggestion logs safely into a dedicated, unlinked list array inside Redis memory
        redis_db.lpush("metrics:meta:platform_suggestions", json.dumps(suggestion_block))
        redis_db.ltrim("metrics:meta:platform_suggestions", 0, 99) # Keep list capped at the 100 most recent records
        return {"status": "SUGGESTION_ACCEPTED_ANONYMOUSLY"}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Failed to log platform improvement metrics.")
