"""Authenticated HTTP adapter for explicit Web↔Telegram identity pairing."""
from __future__ import annotations

from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.identity.pairing import IdentityPairingService
from src.platform.composition import (
    create_identity_link_repository,
    create_identity_pairing_repository,
    create_provider_composition,
)

router = APIRouter(prefix="/civic/identity-pairings", tags=["Identity Pairing"])
_providers = create_provider_composition()
_pairing_service = None
# In-memory repositories are process-local and cannot link independently deployed
# Web and Telegram surfaces. Cross-surface pairing requires shared PostgreSQL.
if _providers.provider_for("external_identity_links") == "postgres":
    _identity_links = create_identity_link_repository(provider_composition=_providers)
    _pairing_repository = create_identity_pairing_repository(
        provider_composition=_providers, identity_link_repository=_identity_links
    )
    _pairing_service = IdentityPairingService(_pairing_repository)


class ConfirmPairingRequest(BaseModel):
    explicit_confirmation: bool = False


@router.post("")
async def issue_pairing(
    response: Response,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, str]:
    """Issue a short-lived code; the caller must be authenticated."""
    if _pairing_service is None:
        raise HTTPException(status_code=503, detail="Cross-surface pairing requires shared PostgreSQL identity persistence")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    challenge = _pairing_service.issue(principal_id=context.principal.principal_id)
    return {
        "pairing_id": challenge.pairing_id,
        "code": challenge.code,
        "expires_at": challenge.expires_at.astimezone(timezone.utc).isoformat(),
        "next_step": "Send /pair followed by this code to Janavani in a private Telegram chat, then explicitly confirm here.",
    }


@router.post("/{pairing_id}/confirm")
async def confirm_pairing(
    pairing_id: str,
    request: ConfirmPairingRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    """Confirm only for the same authenticated principal that issued the code."""
    if _pairing_service is None:
        raise HTTPException(status_code=503, detail="Cross-surface pairing requires shared PostgreSQL identity persistence")
    try:
        identity = _pairing_service.confirm_from_web(
            pairing_id,
            principal_id=context.principal.principal_id,
            explicit_confirmation=request.explicit_confirmation,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "linked": True,
        "provider": identity.provider,
        "authentication_method": identity.authentication_method,
        "verified": identity.verified,
    }
