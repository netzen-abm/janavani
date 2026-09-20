"""Pure civic case lifecycle validation helpers."""
from src.core.case_types import CaseEventType, CaseStatus
from src.core.case_events import CaseEvent
from typing import Iterable

def confirmed_delivery(status: CaseStatus) -> bool:
    return status in {CaseStatus.ACKNOWLEDGED, CaseStatus.FOLLOW_UP, CaseStatus.IN_PROGRESS,
                      CaseStatus.RESPONDED, CaseStatus.RESOLVED, CaseStatus.ESCALATED, CaseStatus.CLOSED}

def validate_event_chain(events: Iterable[CaseEvent]) -> bool:
    previous: CaseEventType | None = None
    seen: set[str] = set()
    case_id: str | None = None
    for event in events:
        if case_id is None:
            case_id = event.case_id
        if event.case_id != case_id or event.event_id in seen:
            return False
        if previous is CaseEventType.ACKNOWLEDGED and event.event_type is CaseEventType.SUBMITTED:
            return False
        if previous is CaseEventType.CLOSED:
            return False
        seen.add(event.event_id)
        previous = event.event_type
    return True
