"""SOS transport/provider dependency boundary."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from src.core.sos import (
    DeliveryRequest,
    DeliveryResult,
    SOSDeliveryState,
    SOSRequest,
    TransportKind,
)


@dataclass(frozen=True)
class SOSDeliveryResult:
    sos_id: str
    state: SOSDeliveryState
    deliveries: tuple[DeliveryResult, ...]


class SOSDeliveryCoordinator:
    """Own transport selection and provider delivery; no policy decisions."""

    def __init__(self, adapters):
        self._adapters = dict(adapters)

    def deliver(self, request: SOSRequest) -> SOSDeliveryResult:
        now = datetime.now(timezone.utc).isoformat()
        payload_ref = self._payload_ref(request)
        deliveries: list[DeliveryResult] = []

        for index, destination_ref in enumerate(request.destination_refs):
            adapter = self._select_adapter(request, index)
            delivery_id = f"delivery-{request.sos_id}-{index}"

            if adapter is None:
                deliveries.append(
                    DeliveryResult(
                        delivery_id=delivery_id,
                        transport_kind=TransportKind.OTHER,
                        state=SOSDeliveryState.UNKNOWN,
                        attempted_at=now,
                        error_code="NO_ELIGIBLE_TRANSPORT",
                    )
                )
                continue

            try:
                deliveries.append(
                    adapter.deliver(
                        DeliveryRequest(
                            delivery_id=delivery_id,
                            sos_id=request.sos_id,
                            destination_ref=destination_ref,
                            payload_ref=payload_ref,
                            transport_kind=adapter.transport_kind,
                            requested_at=now,
                        )
                    )
                )
            except Exception:
                deliveries.append(
                    DeliveryResult(
                        delivery_id=delivery_id,
                        transport_kind=adapter.transport_kind,
                        state=SOSDeliveryState.FAILED,
                        attempted_at=now,
                        error_code="TRANSPORT_EXCEPTION",
                    )
                )

        return SOSDeliveryResult(
            sos_id=request.sos_id,
            state=aggregate_delivery_state(deliveries),
            deliveries=tuple(deliveries),
        )

    def _select_adapter(self, request: SOSRequest, index: int):
        if request.requested_transport_kinds:
            return next(
                (
                    self._adapters[kind]
                    for kind in request.requested_transport_kinds
                    if kind in self._adapters
                ),
                None,
            )
        if not self._adapters:
            return None
        return tuple(self._adapters.values())[index % len(self._adapters)]

    @staticmethod
    def _payload_ref(request: SOSRequest) -> str:
        material = "|".join(
            (request.sos_id, request.incident_context, *request.evidence_refs)
        )
        return f"sos-payload-{sha256(material.encode()).hexdigest()[:32]}"


def aggregate_delivery_state(
    deliveries: list[DeliveryResult],
) -> SOSDeliveryState:
    if not deliveries:
        return SOSDeliveryState.UNKNOWN

    states = {delivery.state for delivery in deliveries}
    for state in (
        SOSDeliveryState.ACKNOWLEDGED,
        SOSDeliveryState.DELIVERED,
        SOSDeliveryState.ACCEPTED,
        SOSDeliveryState.TRANSMITTING,
        SOSDeliveryState.QUEUED,
    ):
        if state in states:
            return state

    if states == {SOSDeliveryState.FAILED}:
        return SOSDeliveryState.FAILED
    return SOSDeliveryState.UNKNOWN
