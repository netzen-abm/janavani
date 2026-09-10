"""Provider-neutral contracts for delivering user-approved document artifacts."""
from __future__ import annotations

from dataclasses import dataclass
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
    case_id: str
    document_id: str
    destination_ref: str
    channel: str
    artifact: DeliveryArtifact


@dataclass(frozen=True)
class DeliveryReceipt:
    """Transport result; it is not by itself proof of acknowledgement."""

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
