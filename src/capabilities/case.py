"""Channel-neutral Case capability contract.

The implementation is intentionally provider-neutral. Access surfaces should
use this boundary instead of reading complaint-specific storage directly.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Protocol


class CaseStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"
    SUBMITTED = "submitted"
    TRACKING = "tracking"
    CLOSED = "closed"
    FAILED = "failed"


@dataclass(frozen=True)
class Case:
    case_id: str
    case_type: str
    status: CaseStatus
    created_at: str
    updated_at: str
    issue: str | None = None
    jurisdiction: Mapping[str, Any] = field(default_factory=dict)
    authority: Mapping[str, Any] | None = None
    evidence_ids: tuple[str, ...] = ()
    document_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseResult:
    ok: bool
    case: Case | None = None
    error_code: str | None = None
    message: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CaseCapability(Protocol):
    def create(self, *, case_type: str, issue: str | None = None, metadata: Mapping[str, Any] | None = None) -> CaseResult: ...
    def get(self, case_id: str) -> CaseResult: ...
    def update(self, case_id: str, **changes: Any) -> CaseResult: ...
    def update_status(self, case_id: str, status: CaseStatus) -> CaseResult: ...
    def delete(self, case_id: str) -> CaseResult: ...
