"""Shared civic case lifecycle contract for the canonical API."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class CaseType(str, Enum):
    COMPLAINT = "complaint"
    GRIEVANCE = "grievance"
    RTI = "rti"
    PETITION = "petition"
    REPRESENTATION = "representation"
    OBJECTION = "objection"
    APPEAL = "appeal"
    OTHER = "other"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESPONDED = "responded"
    ESCALATED = "escalated"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CaseEventType(str, Enum):
    CREATED = "created"
    EDITED = "edited"
    READY = "ready"
    EVIDENCE_ADDED = "evidence_added"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    RESPONSE = "response"
    ESCALATED = "escalated"
    CORRECTION = "correction"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class CaseEvent:
    event_id: str
    case_id: str
    event_type: CaseEventType
    occurred_at: str
    actor_id: str | None = None
    source_channel: str | None = None
    notes: str | None = None


@dataclass
class CivicCase:
    case_id: str
    case_type: CaseType
    subject: str
    narrative: str
    created_by: str | None = None
    related_office_id: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    document_refs: list[str] = field(default_factory=list)
    consent_refs: list[str] = field(default_factory=list)
    status: CaseStatus = CaseStatus.DRAFT
    events: list[CaseEvent] = field(default_factory=list)

    def mark_ready(self, *, event_id: str, occurred_at: str, actor_id: str | None = None) -> CaseEvent:
        if not self.subject.strip() or not self.narrative.strip():
            raise ValueError("A ready case requires a subject and narrative")
        if not self.consent_refs:
            raise ValueError("Submission consent is required before a case can be ready")
        if self.status not in {CaseStatus.DRAFT, CaseStatus.READY}:
            raise ValueError(f"Cannot mark {self.status.value} case ready")
        self.status = CaseStatus.READY
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.READY, occurred_at, actor_id, notes="case_ready"))

    def submit(self, *, event_id: str, occurred_at: str, actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.READY:
            raise ValueError("Only a ready case can be submitted")
        self.status = CaseStatus.SUBMITTED
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.SUBMITTED, occurred_at, actor_id, source_channel))

    def _record(self, event: CaseEvent) -> CaseEvent:
        if event.case_id != self.case_id:
            raise ValueError("Case event belongs to a different case")
        self.events.append(event)
        return event


def validate_event_chain(events: Iterable[CaseEvent]) -> bool:
    previous: CaseEventType | None = None
    for event in events:
        if previous is CaseEventType.ACKNOWLEDGED and event.event_type is CaseEventType.SUBMITTED:
            return False
        if previous is CaseEventType.CLOSED:
            return False
        previous = event.event_type
    return True
