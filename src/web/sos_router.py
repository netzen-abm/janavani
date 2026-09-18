"""HTTP adapter for the canonical Janavani SOS capability.

The route authenticates the caller, creates the shared execution context, and
delegates SOS policy/orchestration to the canonical capability. It does not
implement emergency providers or police/control-room submission.
"""
from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.capabilities.sos import SOSCapability
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.core.sos import SOSRequest, SOSDeliveryState, TransportKind
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity

router = APIRouter(prefix="/api/v1/sos", tags=["SOS"])
_CAPABILITY = SOSCapability()


class SOSTriggerRequest(BaseModel):
    incident_context: str = Field(min_length=1)
    destination_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    location_ref: str | None = None
    explicit_user_choice: bool = False
    remote_transmission: bool = False
    idempotency_key: str | None = None
    requested_transport_kinds: tuple[TransportKind, ...] = ()


@router.post("/trigger")
async def trigger_sos(
    request: SOSTriggerRequest,
    context: IdentityContext = Depends(require_authenticated_identity),
) -> dict[str, object]:
    sos_id = f"sos-{uuid4().hex}"
    side_effect = (
        SideEffectClass.EXTERNAL_SIDE_EFFECT
        if request.remote_transmission
        else SideEffectClass.LOCAL_MUTATION
    )

    if side_effect is SideEffectClass.EXTERNAL_SIDE_EFFECT and not request.idempotency_key:
        raise HTTPException(status_code=422, detail="idempotency_key is required for external SOS operations")

    execution_context = CapabilityExecutionContext.for_capability(
        context,
        capability_id="sos:trigger",
        action="sos:trigger",
        surface="webapp",
        resource_id=sos_id,
        idempotency_key=request.idempotency_key,
        risk_level="high" if request.remote_transmission else "normal",
        side_effect_class=side_effect,
    )

    try:
        result = _CAPABILITY.trigger(
            SOSRequest(
                sos_id=sos_id,
                incident_context=request.incident_context,
                destination_refs=request.destination_refs,
                evidence_refs=request.evidence_refs,
                location_ref=request.location_ref,
                explicit_user_choice=request.explicit_user_choice,
                remote_transmission=request.remote_transmission,
                consequential_action=request.remote_transmission,
                execution_context=execution_context,
                # Approval is intentionally not accepted as a client-supplied boolean.
                # A trusted approval artifact/channel must exist before consequential SOS can execute.
                explicit_user_approval=False,
                requested_transport_kinds=request.requested_transport_kinds,
            ),
            identity=context,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "sos_id": result.sos_id,
        "state": result.state.value,
        "deliveries": [
            {
                "delivery_id": delivery.delivery_id,
                "transport_kind": delivery.transport_kind.value,
                "state": delivery.state.value,
                "provider_reference": delivery.provider_reference,
                "acknowledgement_reference": delivery.acknowledgement_reference,
                "attempted_at": delivery.attempted_at,
                "error_code": delivery.error_code,
            }
            for delivery in result.deliveries
        ],
        "submission": "not_submitted",
        "police_delivery": "not_implemented",
    }
