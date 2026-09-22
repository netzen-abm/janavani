"""Canonical accountability feedback API adapter."""
from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
from src.platform.composition import create_accountability_feedback_repository
from src.utils.feedback_validators import OfficeFeedbackSchema

router = APIRouter(prefix="/api/v1/feedback", tags=["Accountability Feedback Loop"])
INTERFACE_API_KEY_HEADER = APIKeyHeader(name="X-Janavani-Interface-Token", auto_error=True)


def _configured_interface_tokens() -> frozenset[str]:
    raw_tokens = os.getenv("JANAVANI_INTERFACE_TOKENS", "")
    return frozenset(token.strip() for token in raw_tokens.split(",") if token.strip())


def verify_client_token(token: str = Security(INTERFACE_API_KEY_HEADER)) -> str:
    if token not in _configured_interface_tokens():
        raise HTTPException(status_code=403, detail="Unauthorized interface pipeline context.")
    return token


def _capability() -> AccountabilityFeedbackCapability:
    return AccountabilityFeedbackCapability(create_accountability_feedback_repository())


@router.post("/submit", response_model=dict[str, Any])
async def submit_anonymous_office_rating(
    payload: OfficeFeedbackSchema,
    token: str = Security(verify_client_token),
) -> dict[str, Any]:
    """Accept citizen experience reviews through the canonical capability."""
    del token
    feedback = _capability().record(
        office_id=payload.office_id,
        department_name=payload.department_name,
        rating=payload.service_rating,
        issue=payload.citizen_comment,
        source_channel="web",
    )
    return {
        "status": "FEEDBACK_ACCEPTED_ANONYMOUSLY",
        "feedback_id": feedback.feedback_id,
        "office_targeted": feedback.office_id,
    }


@router.get("/summary/{office_id}", response_model=dict[str, Any])
async def fetch_office_performance_summary(
    office_id: str,
    token: str = Security(verify_client_token),
) -> dict[str, Any]:
    """Expose canonical feedback records through the provider-neutral repository."""
    del token
    records = _capability().list_for_office(office_id)
    return {
        "office_id": office_id,
        "aggregate_telemetry": {
            "total_reviews_count": len(records),
            "rating_counts": {
                str(rating): sum(record.rating == rating for record in records)
                for rating in range(1, 6)
            },
        },
        "recent_sanitized_comments": [
            {
                "rating_given": record.rating,
                "comment_body": record.issue,
                "recorded_at": record.submitted_at,
            }
            for record in records[-50:]
        ],
    }
