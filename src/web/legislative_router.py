"""Legislative directory adapter.

JanaVani may prepare civic communication content and identify representative
contact metadata, but it does not email or submit documents on the citizen's
behalf. Any later delivery is outside JanaVani's business boundary.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.representatives_directory import lookup_representatives
from src.storage.cache import TransientStorageEngine

router = APIRouter(
    prefix="/api/v1/legislative",
    tags=["Legislative Communication Core"],
)


class MailDispatchPayload(BaseModel):
    tracking_id: str
    constituency_code: str
    target_tier: str


@router.get("/directory/{constituency_code}", response_model=Dict[str, Any])
async def get_constituency_directory(constituency_code: str):
    """Expose representative metadata to independent frontend adapters."""
    data = lookup_representatives(constituency_code)
    if not data:
        raise HTTPException(
            status_code=404,
            detail="Constituency tracking zone code not registered.",
        )
    return data


@router.post("/dispatch-email", response_model=Dict[str, Any])
async def transmit_letter_to_representative(payload: MailDispatchPayload):
    """Reject the retired email-dispatch capability explicitly."""
    del payload
    raise HTTPException(
        status_code=410,
        detail=(
            "JanaVani does not email or submit documents. "
            "Use the document download capability and take any later action "
            "independently."
        ),
    )
