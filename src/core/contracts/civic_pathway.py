"""Shared contract for selecting a verified civic-action pathway."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CivicPathway(str, Enum):
    COMPLAINT = "complaint"
    RTI = "rti"
    COMPLAINT_AND_RTI = "complaint_and_rti"
    FOLLOW_UP = "follow_up"
    NO_ACTION = "no_action"
    NEEDS_INFORMATION = "needs_information"


@dataclass(frozen=True)
class CivicPathwayDecision:
    pathway: CivicPathway
    reason: str
    trigger_id: Optional[str] = None
    authority_id: Optional[str] = None
    requires_user_confirmation: bool = True
