"""Provider-neutral SOS domain contracts.

This module contains data contracts only. Transport/provider mechanics and
privacy/authorization policy remain outside the domain model.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class SOSDeliveryState(str, Enum):
    LOCAL_ONLY = "LOCAL_ONLY"
    QUEUED = "QUEUED"
    TRANSMITTING = "TRANSMITTING"
    ACCEPTED = "ACCEPTED"
    DELIVERED = "DELIVERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class TransportKind(str, Enum):
    INTERNET = "INTERNET"
    RETICULUM = "RETICULUM"
    LORA = "LORA"
    MESHTASTIC = "MESHTASTIC"
    SATELLITE = "SATELLITE"
    LOCAL = "LOCAL"
    OTHER = "OTHER"


@dataclass(frozen=True)
class SOSRequest:
    sos_id: str
    incident_context: str
    destination_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    location_ref: str | None = None
    explicit_user_choice: bool = False
    remote_transmission: bool = False
    consequential_action: bool = False


@dataclass(frozen=True)
class DeliveryRequest:
    delivery_id: str
    sos_id: str
    destination_ref: str
    payload_ref: str
    transport_kind: TransportKind
    requested_at: str


@dataclass(frozen=True)
class DeliveryResult:
    delivery_id: str
    transport_kind: TransportKind
    state: SOSDeliveryState
    provider_reference: str | None = None
    acknowledgement_reference: str | None = None
    attempted_at: str | None = None
    error_code: str | None = None


class SOSDeliveryAdapter(Protocol):
    """Provider-neutral transport boundary consumed by SOS orchestration."""

    transport_kind: TransportKind

    def deliver(self, request: DeliveryRequest) -> DeliveryResult:
        """Attempt delivery without claiming stronger state than provider evidence supports."""
        ...


class SOSDecisionGate(Protocol):
    """Adapter for the canonical safety/privacy policy boundary.

    The implementation is intentionally external to the SOS capability so
    SOS cannot become a second policy engine.
    """

    def evaluate(self, request: SOSRequest) -> str:
        """Return the canonical policy outcome for this SOS request."""
        ...
