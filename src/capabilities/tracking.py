"""Channel-neutral Case Tracking capability contract and result model."""

from dataclasses import dataclass
from typing import Protocol

from capabilities.case import Case, CaseStatus


@dataclass(frozen=True)
class TrackingResult:
    ok: bool
    case: Case | None = None
    message: str | None = None
    error_code: str | None = None


class CaseTrackingCapability(Protocol):
    def get_status(self, case_id: str) -> TrackingResult: ...
