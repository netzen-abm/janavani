from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from src.core.representatives_directory import lookup_representatives
from src.storage.cache import TransientStorageEngine

router = APIRouter(prefix="/api/v1/legislative", tags=["Legislative Communication Core"])


class DocumentTargetPayload(BaseModel):
    tracking_id: str
    constituency_code: str
    target_tier: str  # 'MP', 'MLA', or 'LSGD'


@router.get("/directory/{constituency_code}", response_model=Dict[str, Any])
async def get_constituency_directory(constituency_code: str):
    """Expose representative directory data to frontend interface channels."""
    data = lookup_representatives(constituency_code)
    if not data:
        raise HTTPException(status_code=404, detail="Constituency tracking zone code not registered in system matrices.")
    return data


@router.post("/document-target", response_model=Dict[str, Any])
async def prepare_document_target(payload: DocumentTargetPayload):
    """Resolve the intended recipient for a document without sending it.

    Janavani prepares documents for citizen review, correction, download and
    printing. It does not dispatch generated documents by email.
    """
    cache_engine = TransientStorageEngine()
    document_data = cache_engine.retrieve_transient_document(payload.tracking_id)
    if not document_data:
        raise HTTPException(status_code=404, detail="Document tracking reference record has expired or does not exist.")

    rep_profile = lookup_representatives(payload.constituency_code)
    if not rep_profile:
        raise HTTPException(status_code=404, detail="Target constituency code map not found.")

    tier_mapping = {
        "MP": (rep_profile["mp_name"], rep_profile["mp_email"]),
        "MLA": (rep_profile["mla_name"], rep_profile["mla_email"]),
        "LSGD": (rep_profile["lsgd_body"], rep_profile["lsgd_email"]),
    }

    if payload.target_tier not in tier_mapping:
        raise HTTPException(status_code=400, detail="Invalid target representative tier specified.")

    recipient_name, recipient_email = tier_mapping[payload.target_tier]
    return {
        "status": "TARGET_RESOLVED_FOR_DOCUMENT",
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "subject_line": document_data.get("subject_line", "Public Grievance Submission"),
        "delivery_mode": "CITIZEN_DOWNLOAD_AND_PRINT_ONLY",
    }
