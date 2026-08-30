"""Persistent case-state contract for the shared civic infrastructure.

Only minimized case metadata and workflow state belong in shared persistence.
Raw personal/sensitive evidence remains on the user's device by design.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class CaseLifecycle(str, Enum):
    OPEN = "open"
    WAITING_FOR_VERIFICATION = "waiting_for_verification"
    WAITING_FOR_TRIGGER = "waiting_for_trigger"
    ACTION_READY = "action_ready"
    CLOSED = "closed"


@dataclass(frozen=True)
class CaseReference:
    case_id: str
    reference_number: str
    created_at: datetime
    lifecycle: CaseLifecycle = CaseLifecycle.OPEN


@dataclass(frozen=True)
class CaseEvent:
    event_id: str
    case_id: str
    event_type: str
    occurred_at: datetime
    summary: str
    sensitive_data_stored_remotely: bool = False
    local_evidence_ref: Optional[str] = None


@dataclass
class PersistentCaseState:
    reference: CaseReference
    events: list[CaseEvent] = field(default_factory=list)
    current_action_id: Optional[str] = None

    def add_event(self, event: CaseEvent) -> None:
        if event.case_id != self.reference.case_id:
            raise ValueError("event belongs to a different case")
        if event.sensitive_data_stored_remotely:
            raise ValueError("raw sensitive data cannot be stored in shared case state")
        self.events.append(event)

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
