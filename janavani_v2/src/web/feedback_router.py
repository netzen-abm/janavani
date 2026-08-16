# Path: janavani_v2/src/web/feedback_router.py
@router.post("/submit")
async def submit_anonymous_office_rating(
    payload: OfficeFeedbackSchema,
    redis_db: redis.Redis = Depends(get_redis_client)
):
    # Verify that the score submission is linked to an authentic Janavani document generation token
    validation_token = f"transient_doc:{payload.verification_token_id}"
    if not redis_db.exists(validation_token):
        raise HTTPException(status_code=403, detail="Review rejected: Invalid or unverified platform action token.")


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import redis
import os

router = APIRouter(prefix="/api/v2/feedback", tags=["Accountability Feedback Loop"])

class HardenedFeedbackSchema(BaseModel):
    office_id: str
    department_name: str
    service_rating: int = Field(..., ge=1, le=5)
    citizen_comment: str
    zk_action_token_id: str # Single-use, platform-signed cryptographic action token

def get_redis_client():
    return redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

@router.post("/submit")
async def submit_authenticated_office_rating(payload: HardenedFeedbackSchema, redis_db: redis.Redis = Depends(get_redis_client)):
    """Accepts office ratings only if they are accompanied by a valid, unexpired platform action token."""
    
    # Verify the token exists in the transient memory cache grid
    token_tracking_key = f"transient_doc:results:{payload.zk_action_token_id}"
    
    if not redis_db.exists(token_tracking_key):
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: Rating submission rejected. You must generate a valid legal document template prior to rating public centers."
        )
        
    # Enforce an single-use validation policy: instantly delete the token to prevent double-voting
    redis_db.delete(token_tracking_key)

    office_score_key = f"feedback:office:{payload.office_id}"
    try:
        redis_db.hincrby(office_score_key, "total_reviews_count", 1)
        redis_db.hincrby(office_score_key, f"rating_star_{payload.service_rating}_count", 1)
        return {"status": "AUTHENTICATED_FEEDBACK_ACCEPTED"}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Cache validation error occurred: {str(e)}")

