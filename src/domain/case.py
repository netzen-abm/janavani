"""Canonical Janavani Case domain object.

A Case is the durable unit of citizen civic work. Transport, AI provider,
and storage implementations must remain outside this domain object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class CaseStatus(str, Enum):
    OPEN = "open"
    UNDERSTANDING = "understanding"
    EVIDENCE_COLLECTION = "evidence_collection"
    AUTHORITY_SELECTION = "authority_selection"
    ACTION_PREPARATION = "action_preparation"
    REVIEW = "review"
    APPROVED = "approved"
    SUBMISSION = "submission"
    TRACKING = "tracking"
    FOLLOW_UP = "follow_up"
    ESCALATION = "escalation"
    OUTCOME = "outcome"
    CLOSED = "closed"
    REOPENED = "reopened"


@dataclass(frozen=True)
class CaseEvent:
    """Append-only domain event metadata; persistence is handled elsewhere."""

    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Case:
    """Channel-neutral civic case state."""

    id: str = field(default_factory=lambda: str(uuid4()))
    issue: str = ""
    status: CaseStatus = CaseStatus.OPEN
    facts: dict[str, Any] = field(default_factory=dict)
    evidence_ids: list[str] = field(default_factory=list)
    document_ids: list[str] = field(default_factory=list)
    authority_ids: list[str] = field(default_factory=list)
    submission_ids: list[str] = field(default_factory=list)
    consent_ids: list[str] = field(default_factory=list)
    events: list[CaseEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.issue = self.issue.strip()
        if not self.issue:
            raise ValueError("case issue is required")

    def transition(self, status: CaseStatus, *, actor: str | None = None, **data: Any) -> None:
        """Apply an explicit status transition and record the transition event."""
        if status == self.status:
            return
        previous = self.status
        self.status = status
        self.events.append(
            CaseEvent(
                event_type="case.status_changed",
                actor=actor,
                data={"from": previous.value, "to": status.value, **data},
            )
        )

    def add_event(self, event_type: str, *, actor: str | None = None, **data: Any) -> None:
        self.events.append(CaseEvent(event_type=event_type, actor=actor, data=data))

    def attach_evidence(self, evidence_id: str, *, actor: str | None = None) -> None:
        """Attach an existing Evidence identity without embedding its content."""
        evidence_id = evidence_id.strip()
        if not evidence_id:
            raise ValueError("evidence_id is required")
        if evidence_id in self.evidence_ids:
            return
        self.evidence_ids.append(evidence_id)
        self.add_event("case.evidence_attached", actor=actor, evidence_id=evidence_id)
