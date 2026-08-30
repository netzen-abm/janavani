"""Shared contracts for procedure-driven case follow-up triggers."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TriggerKind(str, Enum):
    RESPONSE_DEADLINE = "response_deadline"
    NO_RESPONSE = "no_response"
    INADEQUATE_RESPONSE = "inadequate_response"
    USER_REQUESTED = "user_requested"
    EXTERNAL_EVENT = "external_event"


@dataclass(frozen=True)
class FollowUpTrigger:
    trigger_id: str
    kind: TriggerKind
    label: str
    source_id: str
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    interval_days: Optional[int] = None
    requires_verification: bool = True
    notes: str = ""
