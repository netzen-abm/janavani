"""Canonical SOS capability orchestration boundary."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.access.consequential import (
    ConsequentialDecision,
    ConsequentialOperationRequest,
    gate_consequential_operation,
)
from src.capabilities.safety_privacy import (
    AccessPurpose, SafetyPrivacyDecision, SafetyPrivacyRequest, SensitiveResource,
    evaluate_safety_privacy,
)
from src.core.execution import SideEffectClass
from src.core.sos import SOSDeliveryAdapter, SOSDeliveryState, SOSRequest
from src.identity.context import IdentityContext

from src.capabilities.sos_contract import CAPABILITY_ID

@dataclass(frozen=True)
class SOSResult:
    sos_id: str
    state: SOSDeliveryState
    deliveries: tuple[DeliveryResult, ...] = ()

from src.capabilities.sos_safety_gate import CanonicalSOSSafetyPrivacyGate
from src.capabilities.sos_validation import validate_sos_request
from src.capabilities.sos_delivery import SOSDeliveryCoordinator

class SOSCapability:
    """Surface-independent SOS orchestration."""
    def __init__(self, *, decision_gate=None, delivery_adapters=()):
        self._decision_gate = decision_gate or CanonicalSOSSafetyPrivacyGate()
        self._adapters = {a.transport_kind: a for a in delivery_adapters}
        self._delivery = SOSDeliveryCoordinator(self._adapters)

    def trigger(self, request: SOSRequest, *, identity: IdentityContext) -> SOSResult:
        self._validate_request(request, identity=identity)
        if request.consequential_action:
            self._evaluate_consequential_operation(request, identity=identity)
        else:
            self._authorize(request, identity)
        self._check_safety(request, identity)
        if not request.remote_transmission or not request.destination_refs:
            return SOSResult(request.sos_id, SOSDeliveryState.LOCAL_ONLY)
        return self._deliver(request)

    @staticmethod
    def _authorize(request, identity):
        if request.consequential_action:
            return
        decision = authorize(AuthorizationRequest(
            context=identity, capability=CAPABILITY_ID, action=CAPABILITY_ID,
            resource_id=request.sos_id,
        ))
        if decision is AuthorizationDecision.DENY:
            raise PermissionError("Identity is not authorized to trigger SOS")
        if decision is AuthorizationDecision.REQUIRE_APPROVAL:
            raise PermissionError("SOS action requires approval")

    @staticmethod
    def _evaluate_consequential_operation(request, *, identity):
        context = request.execution_context
        if context is None:
            raise ValueError("Consequential SOS requires a CapabilityExecutionContext")
        if context.identity is not identity:
            raise PermissionError("SOS execution identity does not match request identity")
        if context.capability_id != CAPABILITY_ID or context.action != CAPABILITY_ID:
            raise ValueError("SOS execution context does not match capability")
        if context.resource_id not in {None, request.sos_id}:
            raise ValueError("SOS execution context resource does not match request")
        if context.side_effect_class is not SideEffectClass.EXTERNAL_SIDE_EFFECT:
            raise ValueError("Consequential SOS requires an external side-effect context")
        decision = gate_consequential_operation(
            ConsequentialOperationRequest(
                authorization=AuthorizationRequest(
                    context=identity,
                    capability=CAPABILITY_ID,
                    action=CAPABILITY_ID,
                    resource_id=request.sos_id,
                    risk_level=context.risk_level,
                    requires_approval=True,
                    execution_context=context,
                ),
                execution_context=context,
                explicit_user_approval=request.explicit_user_approval,
            )
        )
        if decision is ConsequentialDecision.DENY:
            raise PermissionError("Identity is not authorized to trigger consequential SOS")
        if decision is ConsequentialDecision.CONSENT_REQUIRED:
            raise PermissionError("SOS action requires consent")
        if decision is ConsequentialDecision.REQUIRE_APPROVAL:
            raise PermissionError("SOS action requires approval")

    def _check_safety(self, request, identity):
        decision = self._decision_gate.evaluate(request, identity=identity)
        if decision is not SafetyPrivacyDecision.ALLOW and decision != "ALLOW":
            raise PermissionError(f"SOS safety/privacy decision is {decision}")

    def _deliver(self, request):
        now = datetime.now(timezone.utc).isoformat()
        payload_ref = self._payload_ref(request)
        deliveries = []
        for index, destination_ref in enumerate(request.destination_refs):
            adapter = self._select_adapter(request, index)
            delivery_id = f"delivery-{request.sos_id}-{index}"
            if adapter is None:
                deliveries.append(DeliveryResult(
                    delivery_id=delivery_id, transport_kind=TransportKind.OTHER,
                    state=SOSDeliveryState.UNKNOWN, attempted_at=now,
                    error_code="NO_ELIGIBLE_TRANSPORT",
                ))
                continue
            try:
                deliveries.append(adapter.deliver(DeliveryRequest(
                    delivery_id=delivery_id, sos_id=request.sos_id,
                    destination_ref=destination_ref, payload_ref=payload_ref,
                    transport_kind=adapter.transport_kind, requested_at=now,
                )))
            except Exception:
                deliveries.append(DeliveryResult(
                    delivery_id=delivery_id, transport_kind=adapter.transport_kind,
                    state=SOSDeliveryState.FAILED, attempted_at=now,
                    error_code="TRANSPORT_EXCEPTION",
                ))
        return SOSResult(request.sos_id, self._aggregate_state(deliveries), tuple(deliveries))

    def _validate_request(self, request, *, identity):
        validate_sos_request(request, identity=identity)

    def _deliver(self, request):
        return self._delivery.deliver(request)
