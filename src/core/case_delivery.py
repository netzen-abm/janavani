"""Outcome and citizen-controlled delivery lifecycle for the CivicCase aggregate.

This is a domain boundary, not a second orchestration layer. The aggregate still
owns the state and invariants; this mixin isolates the outcome/delivery lifecycle
from drafting, evidence, and document-reference mutation.
"""
from __future__ import annotations

from src.core.case_events import CaseEvent
from src.core.case_types import (
    CaseEventType,
    CaseStatus,
)


class CivicCaseDeliveryMixin:
    def begin_submission(self, *, event_id: str, occurred_at: str, actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.READY:
            raise ValueError("Only a ready case can begin submission")
        self.status = CaseStatus.SUBMITTING
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.SUBMITTING, occurred_at, actor_id, source_channel))

    def queue_submission(self, *, event_id: str, occurred_at: str, actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        if self.status is not CaseStatus.SUBMITTING:
            raise ValueError("Only a submitting case can be queued")
        self.status = CaseStatus.QUEUED
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.QUEUED, occurred_at, actor_id, source_channel))

    def submit(self, *, event_id: str, occurred_at: str, actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        """Compatibility state transition; it never performs external delivery."""
        if self.status not in {CaseStatus.SUBMITTING, CaseStatus.QUEUED}:
            raise ValueError("Only a submitting or queued case can be marked submitted")
        self.status = CaseStatus.SUBMITTED
        return self._record(CaseEvent(event_id, self.case_id, CaseEventType.SUBMITTED, occurred_at, actor_id, source_channel))

    def report_sent_by_citizen(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        source_channel: str | None = None, notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {CaseStatus.READY, CaseStatus.FOLLOW_UP}:
            raise ValueError("A final document must be ready before the citizen can report sending it")
        self.status = CaseStatus.SUBMITTED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.SENT_BY_CITIZEN,
            occurred_at, actor_id, source_channel, notes=notes,
        ))

    def report_response_received(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        source_channel: str | None = None, source_ref: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {CaseStatus.SUBMITTED, CaseStatus.FOLLOW_UP, CaseStatus.IN_PROGRESS}:
            raise ValueError("A sent case is required before reporting a response")
        self.status = CaseStatus.RESPONDED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.RESPONSE_RECEIVED,
            occurred_at, actor_id, source_channel, source_ref, notes,
        ))

    def report_no_response(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        source_channel: str | None = None, notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {
            CaseStatus.SUBMITTED, CaseStatus.ACKNOWLEDGED,
            CaseStatus.FOLLOW_UP, CaseStatus.IN_PROGRESS,
        }:
            raise ValueError("A sent case is required before reporting no response")
        self.status = CaseStatus.FOLLOW_UP
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.NO_RESPONSE_REPORTED,
            occurred_at, actor_id, source_channel, notes=notes,
        ))

    def acknowledge(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        source_channel: str | None = None, source_ref: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status is not CaseStatus.SUBMITTED:
            raise ValueError("Only a citizen-reported sent case can be acknowledged")
        self.status = CaseStatus.ACKNOWLEDGED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.ACKNOWLEDGED,
            occurred_at, actor_id, source_channel, source_ref, notes,
        ))

    def follow_up(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {CaseStatus.ACKNOWLEDGED, CaseStatus.IN_PROGRESS, CaseStatus.RESPONDED}:
            raise ValueError("Case is not ready for follow-up")
        self.status = CaseStatus.FOLLOW_UP
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.FOLLOW_UP,
            occurred_at, actor_id, notes=notes,
        ))

