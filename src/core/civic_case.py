"""Channel-neutral civic case lifecycle contract.

Web, mobile, DApp and messaging surfaces consume this shared contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


class CaseType(str, Enum):
    COMPLAINT = "complaint"
    GRIEVANCE = "grievance"
    RTI = "rti"
    PETITION = "petition"
    REPRESENTATION = "representation"
    OBJECTION = "objection"
    APPEAL = "appeal"
    CORRUPTION = "corruption"
    MISBEHAVIOUR = "misbehaviour"
    TRANSFER_CONCERN = "transfer_concern"
    OTHER = "other"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    READY = "ready"
    SUBMITTING = "submitting"
    QUEUED = "queued"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    FOLLOW_UP = "follow_up"
    IN_PROGRESS = "in_progress"
    RESPONDED = "responded"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CaseEventType(str, Enum):
    CREATED = "created"
    EDITED = "edited"
    REVIEW_STARTED = "review_started"
    APPROVED = "approved"
    EVIDENCE_ADDED = "evidence_added"
    SUBMITTING = "submitting"
    QUEUED = "queued"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    FOLLOW_UP = "follow_up"
    RESPONSE = "response"
    RESOLVED = "resolved"
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
    source_ref: str | None = None
    notes: str | None = None


@dataclass
class CivicCase:
    case_id: str
    case_type: CaseType
    subject: str
    narrative: str
    created_by: str | None = None
    jurisdiction: dict[str, Any] = field(default_factory=dict)
    related_organisation_id: str | None = None
    related_office_id: str | None = None
    related_official_id: str | None = None
    related_representative_id: str | None = None
    claims: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    document_refs: list[str] = field(default_factory=list)
    consent_refs: list[str] = field(default_factory=list)
    status: CaseStatus = CaseStatus.DRAFT
    events: list[CaseEvent] = field(default_factory=list)

    def edit(self, *, event_id: str, occurred_at: str,
             actor_id: str | None = None, subject: str | None = None,
             narrative: str | None = None) -> CaseEvent:
        self._ensure_editable()
        if subject is not None:
            self.subject = subject.strip()
        if narrative is not None:
            self.narrative = narrative.strip()
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.EDITED, occurred_at, actor_id,
        ))

    def start_review(self, *, event_id: str, occurred_at: str,
                     actor_id: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.DRAFT:
            raise ValueError("Only a draft case can enter review")
        self._ensure_content()
        self.status = CaseStatus.REVIEW
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.REVIEW_STARTED, occurred_at, actor_id,
        ))

    def mark_ready(self, *, event_id: str, occurred_at: str,
                   actor_id: str | None = None) -> CaseEvent:
        if self.status not in {CaseStatus.REVIEW, CaseStatus.READY}:
            raise ValueError(f"Cannot approve {self.status.value} case")
        self._ensure_content()
        if not self.consent_refs:
            raise PermissionError("Explicit submission consent is required")
        self.status = CaseStatus.READY
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.APPROVED, occurred_at, actor_id,
        ))

    def begin_submission(self, *, event_id: str, occurred_at: str,
                         actor_id: str | None = None,
                         source_channel: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.READY:
            raise ValueError("Only a ready case can begin submission")
        self.status = CaseStatus.SUBMITTING
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.SUBMITTING, occurred_at,
            actor_id, source_channel,
        ))

    def queue_submission(self, *, event_id: str, occurred_at: str,
                         actor_id: str | None = None,
                         source_channel: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.SUBMITTING:
            raise ValueError("Only a submitting case can be queued")
        self.status = CaseStatus.QUEUED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.QUEUED, occurred_at,
            actor_id, source_channel,
        ))

    def submit(self, *, event_id: str, occurred_at: str,
               actor_id: str | None = None,
               source_channel: str | None = None) -> CaseEvent:
        if self.status not in {CaseStatus.SUBMITTING, CaseStatus.QUEUED}:
            raise ValueError("Only a submitting or queued case can be submitted")
        self.status = CaseStatus.SUBMITTED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.SUBMITTED, occurred_at,
            actor_id, source_channel,
        ))

    def acknowledge(self, *, event_id: str, occurred_at: str,
                    actor_id: str | None = None,
                    source_channel: str | None = None,
                    source_ref: str | None = None,
                    notes: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.SUBMITTED:
            raise ValueError("Only a submitted case can be acknowledged")
        self.status = CaseStatus.ACKNOWLEDGED
        return self._record(CaseEvent(
            event_id=event_id,
            case_id=self.case_id,
            event_type=CaseEventType.ACKNOWLEDGED,
            occurred_at=occurred_at,
            actor_id=actor_id,
            source_channel=source_channel,
            source_ref=source_ref,
            notes=notes,
        ))

    def follow_up(self, *, event_id: str, occurred_at: str,
                  actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        if self.status not in {
            CaseStatus.ACKNOWLEDGED, CaseStatus.IN_PROGRESS, CaseStatus.RESPONDED,
        }:
            raise ValueError("Case is not ready for follow-up")
        self.status = CaseStatus.FOLLOW_UP
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.FOLLOW_UP, occurred_at,
            actor_id, notes=notes,
        ))

    def respond(self, *, event_id: str, occurred_at: str,
                actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        if self.status not in {
            CaseStatus.ACKNOWLEDGED, CaseStatus.FOLLOW_UP,
            CaseStatus.IN_PROGRESS, CaseStatus.ESCALATED,
        }:
            raise ValueError("Case is not ready for a response")
        self.status = CaseStatus.RESPONDED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.RESPONSE, occurred_at,
            actor_id, notes=notes,
        ))

    def resolve(self, *, event_id: str, occurred_at: str,
                actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.RESPONDED:
            raise ValueError("Only a responded case can be resolved")
        self.status = CaseStatus.RESOLVED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.RESOLVED, occurred_at,
            actor_id, notes=notes,
        ))

    def escalate(self, *, event_id: str, occurred_at: str,
                 actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        if self.status not in {
            CaseStatus.ACKNOWLEDGED, CaseStatus.FOLLOW_UP,
            CaseStatus.IN_PROGRESS, CaseStatus.RESPONDED,
        }:
            raise ValueError("Case is not ready for escalation")
        self.status = CaseStatus.ESCALATED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.ESCALATED, occurred_at,
            actor_id, notes=notes,
        ))

    def close(self, *, event_id: str, occurred_at: str,
              actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        if self.status not in {CaseStatus.RESOLVED, CaseStatus.ESCALATED}:
            raise ValueError("Only resolved or escalated cases can be closed")
        self.status = CaseStatus.CLOSED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.CLOSED, occurred_at,
            actor_id, notes=notes,
        ))

    def add_evidence(self, evidence_id: str, *, event_id: str,
                     occurred_at: str, actor_id: str | None = None,
                     source_channel: str | None = None) -> CaseEvent:
        if self.status in {CaseStatus.CLOSED, CaseStatus.ARCHIVED}:
            raise ValueError("Cannot add evidence to a closed or archived case")
        if evidence_id not in self.evidence_refs:
            self.evidence_refs.append(evidence_id)
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.EVIDENCE_ADDED, occurred_at,
            actor_id, source_channel, evidence_id,
        ))

    def correct(self, *, event_id: str, occurred_at: str,
                actor_id: str | None = None, notes: str | None = None) -> CaseEvent:
        if self.status in {CaseStatus.CLOSED, CaseStatus.ARCHIVED}:
            raise ValueError("Closed or archived cases cannot be corrected")
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.CORRECTION, occurred_at,
            actor_id, notes=notes,
        ))

    def _ensure_content(self) -> None:
        if not self.subject.strip() or not self.narrative.strip():
            raise ValueError("A case requires a subject and narrative")

    def _ensure_editable(self) -> None:
        if self.status in {
            CaseStatus.SUBMITTING, CaseStatus.QUEUED, CaseStatus.SUBMITTED,
            CaseStatus.ACKNOWLEDGED, CaseStatus.IN_PROGRESS,
            CaseStatus.RESPONDED, CaseStatus.RESOLVED, CaseStatus.ESCALATED,
            CaseStatus.CLOSED, CaseStatus.ARCHIVED,
        }:
            raise ValueError("Case is no longer editable")

    def _record(self, event: CaseEvent) -> CaseEvent:
        if event.case_id != self.case_id:
            raise ValueError("Event belongs to a different case")
        if any(existing.event_id == event.event_id for existing in self.events):
            raise ValueError("Duplicate event id")
        self.events.append(event)
        return event

    def confirmed_delivery(self) -> bool:
        return self.status in {
            CaseStatus.ACKNOWLEDGED, CaseStatus.FOLLOW_UP,
            CaseStatus.IN_PROGRESS, CaseStatus.RESPONDED,
            CaseStatus.RESOLVED, CaseStatus.ESCALATED, CaseStatus.CLOSED,
        }


def validate_event_chain(case: CivicCase) -> None:
    seen: set[str] = set()
    previous = ""
    for event in case.events:
        if event.case_id != case.case_id:
            raise ValueError("Event belongs to a different case")
        if event.event_id in seen:
            raise ValueError("Duplicate event id")
        if event.occurred_at < previous:
            raise ValueError("Event timestamps must be chronological")
        seen.add(event.event_id)
        previous = event.occurred_at
