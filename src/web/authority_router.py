"""Authenticated, verified authority lookup API backed by the shared capability."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from src.capabilities.authority import AuthorityLookupRequest
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.web import civic_case_dependencies

router = APIRouter(prefix="/civic/authorities", tags=["Authorities"])


@router.get("/search")
async def search_authorities(
    authority_type: str = Query(..., min_length=1, max_length=80),
    city: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=20),
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    """Return only verified destinations from the canonical Authority capability."""
    authority_type = authority_type.strip()
    city = city.strip()
    if not authority_type or not city:
        raise HTTPException(status_code=422, detail="Authority type and city are required")
    records = civic_case_dependencies.AUTHORITY.search(
        AuthorityLookupRequest(authority_type=authority_type, city=city, limit=limit)
    )
    items = []
    for record in records:
        contact = record.primary_contact
        if not record.verified or contact is None:
            continue
        items.append({
            "authority_id": record.authority_id,
            "name": record.name,
            "authority_type": record.authority_type,
            "city": record.jurisdiction.get("city", ""),
            "state": record.jurisdiction.get("state", ""),
            "destination_name": contact.name,
            "destination_address": contact.address,
            "destination_email": contact.email,
            "destination_role": contact.role,
            "verified": True,
            "last_verified_at": record.last_verified_at,
            "source_refs": list(record.source_refs),
        })
    return {"items": items, "count": len(items)}
