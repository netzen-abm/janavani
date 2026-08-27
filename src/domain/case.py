"""Canonical, channel-neutral civic case domain object.

This module intentionally contains no transport, persistence, AI-provider, or UI
logic. It is the durable domain boundary described by DATA_CONTRACTS.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import uuid4


class CaseType(StrEnum):
    COMPLAINT = "COMPLAINT"
    GRIEVANCE = "GRIEVANCE"
    RTI = "RTI"
    PETITION = "PETITION"
    REPRESENTATION = "REPRESENTATION"
    OBJECTION = "OBJECTION"
    APPEAL = "APPEAL"
    CORRUPTION = "CORRUPTION"
    MISBEHAVIOUR = "MISBEHAVIOUR"
    TRANSFER_CONCERN = "TRANSFER_CONCERN"
    OTHER = "OTHER"


class CaseStatus(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESPONDED = "RESPONDED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True, slots=True)
class CaseEvent:
    """Immutable case history entry."""

    event_id: str
    case_id: str
    event_type: str
    occurred_at: datetime
    actor_id: Optional[str] = None
    source_channel: Optional[str] = None
    source_ref: Optional[str] = None
    notes: Optional[str] = None


@dataclass(slots=True)
class Case:
    """Canonical citizen-work unit shared across Janavani surfaces.

    References deliberately remain opaque identifiers here. Resolution of
    authorities, evidence, documents, identity, and storage belongs to the
    corresponding capability/service layer.
    """

    case_id: str = field(default_factory=lambda: str(uuid4()))
    case_type: CaseType = CaseType.COMPLAINT
    created_by: Optional[str] = None
    subject: str = ""
    narrative: str = ""
    jurisdiction: Optional[str] = None
    related_organisation_id: Optional[str] = None
    related_office_id: Optional[str] = None
    related_official_id: Optional[str] = None
    related_representative_id: Optional[str] = None
    claims: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    document_refs: list[str] = field(default_factory=list)
    consent_refs: list[str] = field(default_factory=list)
    status: CaseStatus = CaseStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[CaseEvent] = field(default_factory=list)

    def add_event(
        self,
        event_type: str,
        *,
        actor_id: Optional[str] = None,
        source_channel: Optional[str] = None,
        source_ref: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> CaseEvent:
        """Append an auditable event and update the case timestamp."""
        now = datetime.now(timezone.utc)
        event = CaseEvent(
            event_id=str(uuid4()),
            case_id=self.case_id,
            event_type=event_type,
            occurred_at=now,
            actor_id=actor_id,
            source_channel=source_channel,
            source_ref=source_ref,
            notes=notes,
        )
        self.events.append(event)
        self.updated_at = now
        return event

    def transition(self, status: CaseStatus, *, actor_id: Optional[str] = None) -> CaseEvent:
        """Move the case to a new state and record the transition.

        This first domain version intentionally does not encode the full
        workflow state machine. Transition policy belongs in the workflow
        capability, while the Case remains the durable product object.
        """
        self.status = status
        return self.add_event(
            status.value,
            actor_id=actor_id,
            notes=f"Case status changed to {status.value}",
        )

    def add_evidence(self, evidence_id: str, *, actor_id: Optional[str] = None) -> CaseEvent:
        if evidence_id not in self.evidence_refs:
            self.evidence_refs.append(evidence_id)
        return self.add_event("EVIDENCE_ADDED", actor_id=actor_id, source_ref=evidence_id)

    def add_document(self, document_id: str, *, actor_id: Optional[str] = None) -> None:
        if document_id not in self.document_refs:
            self.document_refs.append(document_id)
        self.updated_at = datetime.now(timezone.utc)
        self.add_event("DOCUMENT_ADDED", actor_id=actor_id, source_ref=document_id)


__all__ = ["Case", "CaseEvent", "CaseStatus", "CaseType"]
