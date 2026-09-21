"""Contracts for the canonical submission capability."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.civic_case import CivicCase
from src.delivery.contract import DeliveryTransport
from src.identity.context import IdentityContext


@dataclass(frozen=True)
class SubmissionRequest:
    case_id: str
    document_id: str
    destination_ref: str
    consent_scope: str
    source_channel: str | None = None
    artifact_id: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True)
class SubmissionReceipt:
    acknowledgement_ref: str | None = None
    notes: str | None = None


class SubmissionTransport(Protocol):
    def send(
        self, *, case: CivicCase, document_id: str, destination_ref: str
    ) -> SubmissionReceipt: ...


class SubmissionOutcomeUnknown(RuntimeError):
    """External delivery outcome is ambiguous and requires reconciliation."""
