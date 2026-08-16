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
