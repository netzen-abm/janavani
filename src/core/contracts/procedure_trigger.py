"""Contracts for verified civic procedure and trigger data."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    STALE = "stale"


@dataclass(frozen=True)
class ProcedureTrigger:
    trigger_id: str
    action: str
    jurisdiction: str
    condition: str
    trigger: str
    source_id: str
    source_title: str
    source_url: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    verification: VerificationStatus = VerificationStatus.UNVERIFIED
    notes: str = ""

    def is_current(self, on: date) -> bool:
        return (
            self.verification == VerificationStatus.VERIFIED
            and (self.effective_from is None or on >= self.effective_from)
            and (self.effective_to is None or on <= self.effective_to)
        )
