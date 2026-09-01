"""Channel-neutral civic case lifecycle contract."""

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


_ALLOWED_TRANSITIONS: dict[CaseStatus, frozenset[CaseStatus]] = {
    CaseStatus.DRAFT: frozenset({CaseStatus.READY}),
    CaseStatus.READY: frozenset({CaseStatus.SUBMITTED}),
    CaseStatus.SUBMITTED: frozenset({CaseStatus.ACKNOWLEDGED}),
    CaseStatus.ACKNOWLEDGED: frozenset({CaseStatus.IN_PROGRESS}),
    CaseStatus.IN_PROGRESS: frozenset({CaseStatus.RESPONDED, CaseStatus.ESCALATED}),
    CaseStatus.RESPONDED: frozenset({CaseStatus.CLOSED}),
    CaseStatus.ESCALATED: frozenset({CaseStatus.CLOSED}),
    CaseStatus.CLOSED: frozenset({CaseStatus.ARCHIVED}),
    CaseStatus.ARCHIVED: frozenset(),
}


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

    def add_evidence(self, evidence_id: str, *, event_id: str, occurred_at: str,
                     actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        self._ensure_not_terminal()
        if evidence_id not in self.evidence_refs:
            self.evidence_refs.append(evidence_id)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.EVIDENCE_ADDED,
                                      occurred_at, actor_id, source_channel, evidence_id))

    def mark_ready(self, *, event_id: str, occurred_at: str,
                   actor_id: str | None = None) -> CaseEvent:
        if not self.subject.strip() or not self.narrative.strip():
            raise ValueError("A ready case requires a subject and narrative")
        if not self.consent_refs:
            raise PermissionError("Submission consent is required before a case can be ready")
        self._transition(CaseStatus.READY)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.EDITED,
                                      occurred_at, actor_id, None, "case_ready"))

    def submit(self, *, event_id: str, occurred_at: str,
               actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.SUBMITTED)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.SUBMITTED,
                                      occurred_at, actor_id, source_channel))

    def acknowledge(self, *, event_id: str, occurred_at: str,
                    source_channel: str | None = None, notes: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.ACKNOWLEDGED)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.ACKNOWLEDGED,
                                      occurred_at, None, source_channel, notes))

    def start_processing(self, *, event_id: str, occurred_at: str,
                         actor_id: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.IN_PROGRESS)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.EDITED,
                                      occurred_at, actor_id, None, "processing_started"))

    def respond(self, *, event_id: str, occurred_at: str,
                actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.RESPONDED)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.RESPONSE,
                                      occurred_at, actor_id, None, notes))

    def escalate(self, *, event_id: str, occurred_at: str,
                 actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.ESCALATED)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.ESCALATED,
                                      occurred_at, actor_id, None, notes))

    def close(self, *, event_id: str, occurred_at: str,
              actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.CLOSED)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.CLOSED,
                                      occurred_at, actor_id, None, notes))

    def archive(self, *, event_id: str, occurred_at: str,
                actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        self._transition(CaseStatus.ARCHIVED)
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.ARCHIVED,
                                      occurred_at, actor_id, None, notes))

    def _transition(self, target: CaseStatus) -> None:
        if target not in _ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"Invalid case transition: {self.status.value} -> {target.value}")
        self.status = target

    def _ensure_not_terminal(self) -> None:
        if self.status in {CaseStatus.CLOSED, CaseStatus.ARCHIVED}:
            raise ValueError("Cannot modify a closed or archived case")

    def _record(self, event: CaseEvent) -> CaseEvent:
        if event.case_id != self.case_id:
            raise ValueError("Case event belongs to a different case")
        if self.events and event.event_id in {e.event_id for e in self.events}:
            raise ValueError("Duplicate case event id")
        self.events.append(event)
        return event


def confirmed_delivery(status: CaseStatus) -> bool:
    return status in {
        CaseStatus.ACKNOWLEDGED,
        CaseStatus.IN_PROGRESS,
        CaseStatus.RESPONDED,
        CaseStatus.ESCALATED,
        CaseStatus.CLOSED,
    }


def validate_event_chain(events: Iterable[CaseEvent]) -> bool:
    events = list(events)
    if not events:
        return True
    seen: set[str] = set()
    for event in events:
        if event.event_id in seen:
            return False
        seen.add(event.event_id)
    return True
