"""Canonical civic case event value object."""
from dataclasses import dataclass
from src.core.case_types import CaseEventType

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
