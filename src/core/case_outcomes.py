"""Resolution and closure lifecycle for the CivicCase aggregate."""
from __future__ import annotations

from src.core.case_events import CaseEvent
from src.core.case_types import (
    CITIZEN_REOPENED_EVENT,
    CITIZEN_VERIFIED_EVENT,
    CaseEventType,
    CaseStatus,
)
from src.core.case_delivery import CivicCaseDeliveryMixin


class CivicCaseOutcomeMixin(CivicCaseDeliveryMixin):
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

    def respond(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {
            CaseStatus.ACKNOWLEDGED, CaseStatus.FOLLOW_UP,
            CaseStatus.IN_PROGRESS, CaseStatus.ESCALATED,
        }:
            raise ValueError("Case is not ready for a response")
        self.status = CaseStatus.RESPONDED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.RESPONSE,
            occurred_at, actor_id, notes=notes,
        ))

    def resolve(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status is not CaseStatus.RESPONDED:
            raise ValueError("Only a responded case can be resolved")
        self.status = CaseStatus.RESOLVED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.RESOLVED,
            occurred_at, actor_id, notes=notes,
        ))

    def verify_resolution(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        source_channel: str | None = None, source_ref: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status is not CaseStatus.RESOLVED:
            raise ValueError("Only a resolved case can be citizen-verified")
        return self._record(CaseEvent(
            event_id, self.case_id, CITIZEN_VERIFIED_EVENT,
            occurred_at, actor_id, source_channel, source_ref, notes,
        ))

    def reopen_after_citizen_verification(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        source_channel: str | None = None, notes: str | None = None,
    ) -> CaseEvent:
        if self.status is not CaseStatus.RESOLVED:
            raise ValueError("Only a resolved case can be reopened")
        self.status = CaseStatus.FOLLOW_UP
        return self._record(CaseEvent(
            event_id, self.case_id, CITIZEN_REOPENED_EVENT,
            occurred_at, actor_id, source_channel, notes=notes,
        ))

    def citizen_verified_resolution(self) -> bool:
        return any(
            event.event_type is CITIZEN_VERIFIED_EVENT and event.source_ref is not None
            for event in self.events
        )

    def escalate(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {
            CaseStatus.ACKNOWLEDGED, CaseStatus.FOLLOW_UP,
            CaseStatus.IN_PROGRESS, CaseStatus.RESPONDED,
        }:
            raise ValueError("Case is not ready for escalation")
        self.status = CaseStatus.ESCALATED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.ESCALATED,
            occurred_at, actor_id, notes=notes,
        ))

    def close(
        self, *, event_id: str, occurred_at: str, actor_id: str | None = None,
        notes: str | None = None,
    ) -> CaseEvent:
        if self.status not in {CaseStatus.RESOLVED, CaseStatus.ESCALATED}:
            raise ValueError("Only resolved or escalated cases can be closed")
        self.status = CaseStatus.CLOSED
        return self._record(CaseEvent(
            event_id, self.case_id, CaseEventType.CLOSED,
            occurred_at, actor_id, notes=notes,
        ))
