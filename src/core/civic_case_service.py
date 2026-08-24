"""Application service that couples case state changes with audit events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from src.core.civic_case import CivicCase, CaseEvent
from src.storage.repositories.civic_case_events import CivicCaseEventRepository
from src.storage.repositories.civic_case_repository import CivicCaseRepository


class CivicCaseTransitionRepository(Protocol):
    def commit_transition(self, case_id: str, *, access_policy_ref: str, status: str, event: CaseEvent) -> CaseEvent: ...


@dataclass
class CivicCaseService:
    cases: CivicCaseRepository
    events: CivicCaseEventRepository
    transaction: CivicCaseTransitionRepository | None = None
    event_id_factory: Callable[[str, str], str] = lambda case_id, event_type: f"{event_type}:{case_id}"

    def mark_ready(self, case: CivicCase, *, access_policy_ref: str, occurred_at: str, actor_id: str | None = None) -> CaseEvent:
        event = case.mark_ready(event_id=self.event_id_factory(case.case_id, "ready"), occurred_at=occurred_at, actor_id=actor_id)
        return self._commit(case, event, access_policy_ref)

    def submit(self, case: CivicCase, *, access_policy_ref: str, occurred_at: str, actor_id: str | None = None, source_channel: str | None = None) -> CaseEvent:
        event = case.submit(event_id=self.event_id_factory(case.case_id, "submitted"), occurred_at=occurred_at, actor_id=actor_id, source_channel=source_channel)
        return self._commit(case, event, access_policy_ref)

    def _commit(self, case: CivicCase, event: CaseEvent, access_policy_ref: str) -> CaseEvent:
        if self.transaction is not None:
            return self.transaction.commit_transition(case.case_id, access_policy_ref=access_policy_ref, status=case.status.value, event=event)
        self.cases.save(case, access_policy_ref=access_policy_ref)
        self.events.append(event, access_policy_ref=access_policy_ref)
        return event
