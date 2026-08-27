"""Canonical submission and delivery state model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class SubmissionStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    TRANSMITTING = "transmitting"
    SENT = "sent"
    RECEIVED = "received"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DeliveryEvent:
    status: SubmissionStatus
    occurred_at: datetime
    adapter_id: str | None = None
    reference: str | None = None
    reason: str | None = None


@dataclass
class Submission:
    case_id: str
    destination_ref: str
    operation_id: str = field(default_factory=lambda: f"OP-{uuid4().hex[:12].upper()}")
    submission_id: str = field(default_factory=lambda: f"SUB-{uuid4().hex[:12].upper()}")
    status: SubmissionStatus = SubmissionStatus.CREATED
    consent_ref: str | None = None
    authorization_ref: str | None = None
    payload_hash: str | None = None
    events: list[DeliveryEvent] = field(default_factory=list)

    def transition(self, status: SubmissionStatus, *, adapter_id: str | None = None, reference: str | None = None, reason: str | None = None, occurred_at: datetime | None = None) -> None:
        allowed = {
            SubmissionStatus.CREATED: {SubmissionStatus.QUEUED, SubmissionStatus.CANCELLED, SubmissionStatus.EXPIRED},
            SubmissionStatus.QUEUED: {SubmissionStatus.TRANSMITTING, SubmissionStatus.CANCELLED, SubmissionStatus.EXPIRED, SubmissionStatus.FAILED},
            SubmissionStatus.TRANSMITTING: {SubmissionStatus.SENT, SubmissionStatus.FAILED, SubmissionStatus.UNKNOWN, SubmissionStatus.EXPIRED},
            SubmissionStatus.SENT: {SubmissionStatus.RECEIVED, SubmissionStatus.ACKNOWLEDGED, SubmissionStatus.FAILED, SubmissionStatus.UNKNOWN},
            SubmissionStatus.RECEIVED: {SubmissionStatus.ACKNOWLEDGED, SubmissionStatus.UNKNOWN},
            SubmissionStatus.ACKNOWLEDGED: set(),
            SubmissionStatus.FAILED: {SubmissionStatus.QUEUED, SubmissionStatus.UNKNOWN},
            SubmissionStatus.EXPIRED: set(),
            SubmissionStatus.CANCELLED: set(),
            SubmissionStatus.UNKNOWN: {SubmissionStatus.QUEUED, SubmissionStatus.SENT, SubmissionStatus.RECEIVED, SubmissionStatus.ACKNOWLEDGED, SubmissionStatus.FAILED},
        }
        if status not in allowed[self.status]:
            raise ValueError(f"invalid submission transition: {self.status.value} -> {status.value}")
        if status in {SubmissionStatus.SENT, SubmissionStatus.RECEIVED, SubmissionStatus.ACKNOWLEDGED} and not reference:
            raise ValueError(f"{status.value} requires provider/delivery reference")
        self.status = status
        self.events.append(DeliveryEvent(status, occurred_at or datetime.now(timezone.utc), adapter_id, reference, reason))

    def can_retry(self) -> bool:
        return self.status in {SubmissionStatus.FAILED, SubmissionStatus.UNKNOWN}


__all__ = ["DeliveryEvent", "Submission", "SubmissionStatus"]
