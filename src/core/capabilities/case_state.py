"""In-memory reference implementation of the shared case-state repository.

The interface is deliberately storage-neutral so encrypted/local or remote
metadata stores can be introduced without changing civic capabilities.
"""

from __future__ import annotations

from uuid import uuid4

from src.core.contracts.case_state import CaseEvent, CaseLifecycle, CaseReference, PersistentCaseState


class SharedCaseStateRepository:
    def __init__(self):
        self._cases: dict[str, PersistentCaseState] = {}

    def create(self, reference_number: str) -> PersistentCaseState:
        case_id = f"case-{uuid4().hex[:16]}"
        case = PersistentCaseState(CaseReference(case_id, reference_number, PersistentCaseState.now()))
        self._cases[case_id] = case
        return case

    def get(self, case_id: str) -> PersistentCaseState:
        return self._cases[case_id]

    def add_event(self, case_id: str, event_type: str, summary: str, *, local_evidence_ref: str | None = None) -> CaseEvent:
        case = self.get(case_id)
        event = CaseEvent(
            event_id=f"evt-{uuid4().hex[:12]}",
            case_id=case_id,
            event_type=event_type,
            occurred_at=PersistentCaseState.now(),
            summary=summary,
            local_evidence_ref=local_evidence_ref,
        )
        case.add_event(event)
        return event

    def set_lifecycle(self, case_id: str, lifecycle: CaseLifecycle) -> PersistentCaseState:
        case = self.get(case_id)
        case.reference = CaseReference(
            case.reference.case_id,
            case.reference.reference_number,
            case.reference.created_at,
            lifecycle,
        )
        return case
