"""Provider-neutral contracts for delivering user-approved document artifacts."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


@dataclass(frozen=True)
class DeliveryArtifact:
    """Immutable artifact payload prepared for an external delivery adapter."""

    artifact_id: str
    document_id: str
    case_id: str
    format: str
    content: bytes
    content_sha256: str
    media_type: str


@dataclass(frozen=True)
class DeliveryRequest:
    """Provider-neutral request sent from the canonical submission boundary."""

    submission_id: str
    idempotency_key: str
    case_id: str
    document_id: str
    destination_ref: str
    channel: str
    artifact: DeliveryArtifact

    def __post_init__(self) -> None:
        if not self.submission_id.strip():
            raise ValueError("submission_id is required")
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        if not self.case_id.strip():
            raise ValueError("case_id is required")
        if not self.document_id.strip():
            raise ValueError("document_id is required")
        if not self.destination_ref.strip():
            raise ValueError("destination_ref is required")
        if not self.channel.strip():
            raise ValueError("channel is required")


class DeliveryOutcome(str, Enum):
    """Provider-neutral transport outcome before acknowledgement evidence."""

    SUBMITTED = "submitted"
    UNKNOWN = "unknown"
    FAILED = "failed"


class DeliveryTransportError(RuntimeError):
    """A delivery adapter could not complete cleanly and reports its outcome."""

    def __init__(self, message: str, *, outcome: DeliveryOutcome = DeliveryOutcome.UNKNOWN) -> None:
        super().__init__(message)
        if outcome not in {DeliveryOutcome.UNKNOWN, DeliveryOutcome.FAILED}:
            raise ValueError("Transport errors may only report unknown or failed")
        self.outcome = outcome


@dataclass(frozen=True)
class DeliveryReceipt:
    """Transport result; it is not by itself proof of acknowledgement."""

    outcome: DeliveryOutcome = DeliveryOutcome.SUBMITTED
    external_reference: str | None = None
    transport_reference: str | None = None
    acknowledgement_evidence_ref: str | None = None
    notes: str | None = None


class DeliveryTransport(Protocol):
    """Adapter contract for an external destination/channel."""

    def deliver(self, request: DeliveryRequest) -> DeliveryReceipt:
        """Attempt external delivery and return the transport result."""
        ...


class DeliveryArtifactResolver(Protocol):
    """Resolve a specific approved artifact into immutable delivery bytes."""

    def resolve(self, *, artifact_id: str, case_id: str, document_id: str) -> DeliveryArtifact:
        """Fail closed unless the artifact belongs to the case/document and is approved."""
        ...
