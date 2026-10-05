"""SOS transport/provider dependency boundary."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from src.core.sos import DeliveryRequest, DeliveryResult, SOSDeliveryState

class SOSDeliveryCoordinator:
    def __init__(self, adapters):
        self._adapters = dict(adapters)

    def deliver(self, request):
        now = datetime.now(timezone.utc).isoformat()
        payload_ref = self._payload_ref(request)
        deliveries = []
        for index, destination_ref in enumerate(request.destination_refs):
            adapter = self._select_adapter(request, index)
            delivery_id = f"delivery-{request.sos_id}-{index}"
            if adapter is None:
                deliveries.append(DeliveryResult(delivery_id=delivery_id, transport_kind="other", state=SOSDeliveryState.UNKNOWN, attempted_at=now, error_code="NO_ELIGIBLE_TRANSPORT"))
                continue
            try:
                deliveries.append(adapter.deliver(DeliveryRequest(
                    delivery_id=delivery_id, sos_id=request.sos_id, destination_ref=destination_ref,
                    payload_ref=payload_ref, transport_kind=adapter.transport_kind, requested_at=now,
                )))
            except Exception:
                deliveries.append(DeliveryResult(
                    delivery_id=delivery_id, transport_kind=adapter.transport_kind,
                    state=SOSDeliveryState.FAILED, attempted_at=now, error_code="TRANSPORT_EXCEPTION",
                ))
        return SOSDeliveryResult(request.sos_id, aggregate_delivery_state(deliveries), tuple(deliveries))

    def _select_adapter(self, request, index):
        if request.requested_transport_kinds:
            return next((self._adapters[k] for k in request.requested_transport_kinds if k in self._adapters), None)
        if not self._adapters:
            return None
        return tuple(self._adapters.values())[index % len(self._adapters)]

    @staticmethod
    def _payload_ref(request):
        material = "|".join((request.sos_id, request.incident_context, *request.evidence_refs))
        return f"sos-payload-{sha256(material.encode()).hexdigest()[:32]}"

def aggregate_delivery_state(deliveries):
    if not deliveries:
        return SOSDeliveryState.UNKNOWN
    states = {d.state for d in deliveries}
    for state in (SOSDeliveryState.ACKNOWLEDGED, SOSDeliveryState.DELIVERED, SOSDeliveryState.ACCEPTED, SOSDeliveryState.TRANSMITTING, SOSDeliveryState.QUEUED):
        if state in states:
            return state
    return SOSDeliveryState.FAILED if states == {SOSDeliveryState.FAILED} else SOSDeliveryState.UNKNOWN

class SOSDeliveryResult:
    def __init__(self, sos_id, state, deliveries):
        self.sos_id = sos_id
        self.state = state
        self.deliveries = deliveries
