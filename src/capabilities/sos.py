"""Canonical SOS capability orchestration boundary."""
from __future__ import annotations

from dataclasses import dataclass

from src.access.authorization import (
    AuthorizationDecision,
    AuthorizationRequest,
    authorize,
)
from src.access.consequential import (
    ConsequentialDecision,
    ConsequentialOperationRequest,
    gate_consequential_operation,
)
from src.capabilities.safety_privacy import SafetyPrivacyDecision
from src.capabilities.sos_contract import CAPABILITY_ID
from src.capabilities.sos_delivery import SOSDeliveryCoordinator
from src.capabilities.sos_safety_gate import CanonicalSOSSafetyPrivacyGate
from src.capabilities.sos_validation import validate_sos_request
from src.core.sos import DeliveryResult, SOSDeliveryState, SOSRequest
from src.identity.context import IdentityContext


@dataclass(frozen=True)
class SOSResult:
    sos_id: str
    state: SOSDeliveryState
    deliveries: tuple[DeliveryResult, ...] = ()


class SOSCapability:
    """Surface-independent SOS orchestration."""

    def __init__(self, *, decision_gate=None, delivery_adapters=()):
        self._decision_gate = decision_gate or CanonicalSOSSafetyPrivacyGate()
        adapters = {adapter.transport_kind: adapter for adapter in delivery_adapters}
        self._delivery = SOSDeliveryCoordinator(adapters)

    def trigger(self, request: SOSRequest, *, identity: IdentityContext) -> SOSResult:
        validate_sos_request(request, identity=identity)
        if request.consequential_action:
            self._evaluate_consequential_operation(request, identity=identity)
        else:
            self._authorize(request, identity)
        self._check_safety(request, identity)

        if not request.remote_transmission or not request.destination_refs:
            return SOSResult(request.sos_id, SOSDeliveryState.LOCAL_ONLY)

        return self._deliver(request)

    @staticmethod
    def _authorize(request: SOSRequest, identity: IdentityContext) -> None:
        decision = authorize(
            AuthorizationRequest(
                context=identity,
                capability=CAPABILITY_ID,
                action=CAPABILITY_ID,
                resource_id=request.sos_id,
            )
        )
        if decision is AuthorizationDecision.DENY:
            raise PermissionError("Identity is not authorized to trigger SOS")
        if decision is AuthorizationDecision.REQUIRE_APPROVAL:
            raise PermissionError("SOS action requires approval")

    @staticmethod
    def _evaluate_consequential_operation(
        request: SOSRequest, *, identity: IdentityContext
    ) -> None:
        context = request.execution_context
        if context is None:
            raise ValueError(
                "Consequential SOS requires a CapabilityExecutionContext"
            )
        if context.identity is not identity:
            raise PermissionError(
                "SOS execution identity does not match request identity"
            )
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
            raise PermissionError(
                "Identity is not authorized to trigger consequential SOS"
            )
        if decision is ConsequentialDecision.CONSENT_REQUIRED:
            raise PermissionError("SOS action requires consent")
        if decision is ConsequentialDecision.REQUIRE_APPROVAL:
            raise PermissionError("SOS action requires approval")

    def _check_safety(self, request: SOSRequest, identity: IdentityContext) -> None:
        decision = self._decision_gate.evaluate(request, identity=identity)
        if decision is not SafetyPrivacyDecision.ALLOW and decision != "ALLOW":
            raise PermissionError(f"SOS safety/privacy decision is {decision}")

    def _deliver(self, request: SOSRequest) -> SOSResult:
        result = self._delivery.deliver(request)
        return SOSResult(
            sos_id=result.sos_id,
            state=result.state,
            deliveries=result.deliveries,
        )
