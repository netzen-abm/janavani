"""Canonical, truthful civic-submission and delivery state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import uuid4


class SubmissionStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SUBMISSION_ATTEMPTED = "SUBMISSION_ATTEMPTED"
    QUEUED = "QUEUED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class SubmissionEvent:
    event_id: str
    submission_id: str
    status: SubmissionStatus
    occurred_at: datetime
    provider_ref: Optional[str] = None
    notes: Optional[str] = None


@dataclass(slots=True)
class Submission:
    """A durable attempt to deliver a citizen-approved case artifact.

    Local persistence or generation of an artifact never implies external
    delivery. Confirmation must be represented by an explicit event/provider
    reference when available.
    """

    submission_id: str = field(default_factory=lambda: str(uuid4()))
    case_id: str = ""
    document_id: Optional[str] = None
    destination_ref: Optional[str] = None
    channel: Optional[str] = None
    status: SubmissionStatus = SubmissionStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[SubmissionEvent] = field(default_factory=list)

    def transition(
        self,
        status: SubmissionStatus,
        *,
        provider_ref: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> SubmissionEvent:
        """Record a delivery state transition with optional external evidence."""
        now = datetime.now(timezone.utc)
        event = SubmissionEvent(
            event_id=str(uuid4()),
            submission_id=self.submission_id,
            status=status,
            occurred_at=now,
            provider_ref=provider_ref,
            notes=notes,
        )
        self.status = status
        self.updated_at = now
        self.events.append(event)
        return event

    def confirm(self, *, provider_ref: str, notes: Optional[str] = None) -> SubmissionEvent:
        """Confirm only with an explicit provider/external reference."""
        if not provider_ref.strip():
            raise ValueError("provider_ref is required for confirmed delivery")
        return self.transition(
            SubmissionStatus.CONFIRMED,
            provider_ref=provider_ref,
            notes=notes,
        )


__all__ = ["Submission", "SubmissionEvent", "SubmissionStatus"]
