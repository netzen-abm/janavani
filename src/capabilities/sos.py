"""Canonical SOS capability orchestration boundary.

The capability coordinates authorization, the canonical safety/privacy gate,
and provider-neutral delivery adapters. It does not implement transport or
create a competing policy engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.sos import (
    DeliveryRequest,
    DeliveryResult,
    SOSDeliveryAdapter,
    SOSDeliveryState,
    SOSRequest,
    TransportKind,
)
from src.identity.context import IdentityContext

CAPABILITY_ID = "sos:trigger"


@dataclass(frozen=True)
class SOSResult:
    sos_id: str
    state: SOSDeliveryState
    deliveries: tuple[DeliveryResult, ...] = ()


class SOSCapability:
    """Surface-independent SOS orchestration."""

    def __init__(self, *, decision_gate, delivery_adapters: tuple[SOSDeliveryAdapter, ...] = ()) -> None:
        self._decision_gate = decision_gate
        self._adapters = {adapter.transport_kind: adapter for adapter in delivery_adapters}

    def trigger(self, request: SOSRequest, *, identity: IdentityContext) -> SOSResult:
        """Authorize and execute an SOS request without claiming unverified delivery."""
        self._validate_request(request)

        decision = authorize(AuthorizationRequest(
            context=identity,
            capability=CAPABILITY_ID,
            action="sos:trigger",
            resource_id=request.sos_id,
            requires_approval=request.consequential_action,
        ))
        if decision is AuthorizationDecision.DENY:
            raise PermissionError("Identity is not authorized to trigger SOS")
        if decision is AuthorizationDecision.REQUIRE_APPROVAL:
            raise PermissionError("SOS action requires approval")

        policy_outcome = self._decision_gate.evaluate(request, identity=identity)
        if policy_outcome != "ALLOW":
            raise PermissionError(f"SOS safety/privacy decision is {policy_outcome}")

        if not request.remote_transmission or not request.destination_refs:
            return SOSResult(sos_id=request.sos_id, state=SOSDeliveryState.LOCAL_ONLY)

        payload_ref = self._payload_ref(request)
        deliveries: list[DeliveryResult] = []
        now = datetime.now(timezone.utc).isoformat()
        for index, destination_ref in enumerate(request.destination_refs):
            adapter = self._select_adapter(index)
            if adapter is None:
                deliveries.append(DeliveryResult(
                    delivery_id=f"delivery-{request.sos_id}-{index}",
                    transport_kind=TransportKind.OTHER,
                    state=SOSDeliveryState.UNKNOWN,
                    attempted_at=now,
                    error_code="NO_ELIGIBLE_TRANSPORT",
                ))
                continue
            delivery_request = DeliveryRequest(
                delivery_id=f"delivery-{request.sos_id}-{index}",
                sos_id=request.sos_id,
                destination_ref=destination_ref,
                payload_ref=payload_ref,
                transport_kind=adapter.transport_kind,
                requested_at=now,
            )
            try:
                deliveries.append(adapter.deliver(delivery_request))
            except Exception:
                deliveries.append(DeliveryResult(
                    delivery_id=delivery_request.delivery_id,
                    transport_kind=adapter.transport_kind,
                    state=SOSDeliveryState.FAILED,
                    attempted_at=now,
                    error_code="TRANSPORT_EXCEPTION",
                ))

        return SOSResult(
            sos_id=request.sos_id,
            state=self._aggregate_state(deliveries),
            deliveries=tuple(deliveries),
        )

    @staticmethod
    def _validate_request(request: SOSRequest) -> None:
        if not request.sos_id.strip():
            raise ValueError("sos_id is required")
        if not request.incident_context.strip():
            raise ValueError("incident_context is required")
        if not request.explicit_user_choice:
            raise PermissionError("Explicit user choice is required")
        if request.remote_transmission and not request.destination_refs:
            raise ValueError("A destination is required for remote transmission")

    def _select_adapter(self, index: int) -> SOSDeliveryAdapter | None:
        if not self._adapters:
            return None
        # Selection is intentionally deterministic for the contract tests. A
        # future policy/routing capability may choose among eligible adapters.
        return tuple(self._adapters.values())[index % len(self._adapters)]

    @staticmethod
    def _payload_ref(request: SOSRequest) -> str:
        material = "|".join((request.sos_id, request.incident_context, *request.evidence_refs))
        return f"sos-payload-{sha256(material.encode()).hexdigest()[:32]}"

    @staticmethod
    def _aggregate_state(deliveries: list[DeliveryResult]) -> SOSDeliveryState:
        if not deliveries:
            return SOSDeliveryState.UNKNOWN
        states = {delivery.state for delivery in deliveries}
        if SOSDeliveryState.ACKNOWLEDGED in states:
            return SOSDeliveryState.ACKNOWLEDGED
        if SOSDeliveryState.DELIVERED in states:
            return SOSDeliveryState.DELIVERED
        if SOSDeliveryState.ACCEPTED in states:
            return SOSDeliveryState.ACCEPTED
        if SOSDeliveryState.TRANSMITTING in states:
            return SOSDeliveryState.TRANSMITTING
        if SOSDeliveryState.QUEUED in states:
            return SOSDeliveryState.QUEUED
        if states == {SOSDeliveryState.FAILED}:
            return SOSDeliveryState.FAILED
        return SOSDeliveryState.UNKNOWN
