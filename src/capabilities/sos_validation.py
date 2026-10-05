"""SOS request trust validation boundary."""
from __future__ import annotations
from src.core.execution import SideEffectClass
from src.capabilities.sos import CAPABILITY_ID

def validate_sos_request(request, *, identity):
    if not request.sos_id.strip() or not request.incident_context.strip():
        raise ValueError("sos_id and incident_context are required")
    if not request.explicit_user_choice:
        raise PermissionError("Explicit user choice is required")
    if request.remote_transmission and not request.destination_refs:
        raise ValueError("A destination is required for remote transmission")
    context = request.execution_context
    if context is not None and context.identity is not identity:
        raise PermissionError("SOS execution identity does not match request identity")
    if request.consequential_action:
        if context is None:
            raise ValueError("Consequential SOS requires a CapabilityExecutionContext")
        if context.capability_id != CAPABILITY_ID or context.action != CAPABILITY_ID:
            raise ValueError("SOS execution context does not match capability")
        if context.resource_id not in {None, request.sos_id}:
            raise ValueError("SOS execution context resource does not match request")
        if context.side_effect_class is not SideEffectClass.EXTERNAL_SIDE_EFFECT:
            raise ValueError("Consequential SOS requires an external side-effect context")
