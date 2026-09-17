from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.capabilities.sos import CAPABILITY_ID, SOSCapability
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.core.sos import (
    DeliveryRequest,
    DeliveryResult,
    SOSDeliveryState,
    SOSRequest,
    TransportKind,
)
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal


class AllowGate:
    def evaluate(self, request: SOSRequest, *, identity: IdentityContext) -> str:
        assert identity.principal.principal_id == "citizen-1"
        return "ALLOW"


@dataclass
class FakeTransport:
    transport_kind: TransportKind = TransportKind.LOCAL
    result_state: SOSDeliveryState = SOSDeliveryState.ACCEPTED

    def deliver(self, request: DeliveryRequest) -> DeliveryResult:
        return DeliveryResult(
            delivery_id=request.delivery_id,
            transport_kind=self.transport_kind,
            state=self.result_state,
            attempted_at=request.requested_at,
            provider_reference="provider-ref",
        )


def identity() -> IdentityContext:
    return IdentityContext(Principal(
        principal_id="citizen-1",
        identity_mode=IdentityMode.AUTHENTICATED,
        interface="test",
        capabilities=frozenset({CAPABILITY_ID}),
    ))


def request(**overrides) -> SOSRequest:
    values = {
        "sos_id": "sos-1",
        "incident_context": "unsafe travel",
        "explicit_user_choice": True,
    }
    values.update(overrides)
    return SOSRequest(**values)


def consequential_context(identity_context: IdentityContext) -> CapabilityExecutionContext:
    return CapabilityExecutionContext.for_capability(
        identity_context,
        capability_id=CAPABILITY_ID,
        action="sos:trigger",
        surface="test",
        resource_id="sos-1",
        idempotency_key="idem-sos-1",
        risk_level="high",
        side_effect_class=SideEffectClass.EXTERNAL_SIDE_EFFECT,
    )


def test_local_sos_does_not_claim_delivery() -> None:
    result = SOSCapability(decision_gate=AllowGate()).trigger(request(), identity=identity())
    assert result.state is SOSDeliveryState.LOCAL_ONLY
    assert result.deliveries == ()


def test_default_sos_uses_canonical_safety_privacy_gate() -> None:
    result = SOSCapability().trigger(request(), identity=identity())
    assert result.state is SOSDeliveryState.LOCAL_ONLY


def test_remote_sos_without_transport_is_unknown() -> None:
    result = SOSCapability(decision_gate=AllowGate()).trigger(
        request(remote_transmission=True, destination_refs=("trusted-contact-1",)),
        identity=identity(),
    )
    assert result.state is SOSDeliveryState.UNKNOWN
    assert result.deliveries[0].error_code == "NO_ELIGIBLE_TRANSPORT"


def test_provider_acceptance_is_not_delivery() -> None:
    adapter = FakeTransport(result_state=SOSDeliveryState.ACCEPTED)
    result = SOSCapability(
        decision_gate=AllowGate(), delivery_adapters=(adapter,)
    ).trigger(
        request(remote_transmission=True, destination_refs=("trusted-contact-1",)),
        identity=identity(),
    )
    assert result.state is SOSDeliveryState.ACCEPTED
    assert result.state is not SOSDeliveryState.DELIVERED


def test_acknowledgement_is_stronger_than_delivery() -> None:
    adapter = FakeTransport(result_state=SOSDeliveryState.ACKNOWLEDGED)
    result = SOSCapability(
        decision_gate=AllowGate(), delivery_adapters=(adapter,)
    ).trigger(
        request(remote_transmission=True, destination_refs=("trusted-contact-1",)),
        identity=identity(),
    )
    assert result.state is SOSDeliveryState.ACKNOWLEDGED


def test_missing_explicit_choice_is_rejected_before_policy_gate() -> None:
    with pytest.raises(PermissionError, match="Explicit user choice"):
        SOSCapability(decision_gate=AllowGate()).trigger(
            request(explicit_user_choice=False), identity=identity()
        )


def test_policy_denial_is_not_bypassed() -> None:
    class DenyGate:
        def evaluate(self, request: SOSRequest, *, identity: IdentityContext) -> str:
            assert identity.principal.principal_id == "citizen-1"
            return "BLOCK"

    with pytest.raises(PermissionError, match="BLOCK"):
        SOSCapability(decision_gate=DenyGate()).trigger(request(), identity=identity())


def test_transport_exception_becomes_failed_state() -> None:
    class BrokenTransport(FakeTransport):
        def deliver(self, request: DeliveryRequest) -> DeliveryResult:
            raise RuntimeError("offline")

    result = SOSCapability(
        decision_gate=AllowGate(), delivery_adapters=(BrokenTransport(),)
    ).trigger(
        request(remote_transmission=True, destination_refs=("trusted-contact-1",)),
        identity=identity(),
    )
    assert result.state is SOSDeliveryState.FAILED
    assert result.deliveries[0].error_code == "TRANSPORT_EXCEPTION"


def test_requested_transport_is_honored() -> None:
    local = FakeTransport(transport_kind=TransportKind.LOCAL)
    internet = FakeTransport(transport_kind=TransportKind.INTERNET)
    result = SOSCapability(
        decision_gate=AllowGate(), delivery_adapters=(local, internet)
    ).trigger(
        request(
            remote_transmission=True,
            destination_refs=("trusted-contact-1",),
            requested_transport_kinds=(TransportKind.INTERNET,),
        ),
        identity=identity(),
    )
    assert result.deliveries[0].transport_kind is TransportKind.INTERNET


def test_unavailable_requested_transport_is_unknown() -> None:
    result = SOSCapability(
        decision_gate=AllowGate(),
        delivery_adapters=(FakeTransport(transport_kind=TransportKind.LOCAL),),
    ).trigger(
        request(
            remote_transmission=True,
            destination_refs=("trusted-contact-1",),
            requested_transport_kinds=(TransportKind.INTERNET,),
        ),
        identity=identity(),
    )
    assert result.state is SOSDeliveryState.UNKNOWN
    assert result.deliveries[0].error_code == "NO_ELIGIBLE_TRANSPORT"


def test_consequential_action_requires_canonical_approval() -> None:
    identity_context = identity()
    with pytest.raises(PermissionError, match="SafetyPrivacyDecision.REVIEW"):
        SOSCapability().trigger(
            request(
                consequential_action=True,
                execution_context=consequential_context(identity_context),
            ),
            identity=identity_context,
        )


def test_consequential_action_with_approval_can_reach_sos_gate() -> None:
    identity_context = identity()
    result = SOSCapability(decision_gate=AllowGate()).trigger(
        request(
            consequential_action=True,
            execution_context=consequential_context(identity_context),
            explicit_user_approval=True,
        ),
        identity=identity_context,
    )
    assert result.state is SOSDeliveryState.LOCAL_ONLY
