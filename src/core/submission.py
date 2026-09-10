"""Canonical submission persistence value object and repository contract."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class SubmissionRecord:
    """Durable delivery facts; acknowledgement is evidence, not inferred state."""

    submission_id: str
    case_id: str
    destination_ref: str
    document_ref: str | None
    channel: str
    state: str
    attempted_at: str | None = None
    submitted_at: str | None = None
    acknowledged_at: str | None = None
    external_reference: str | None = None
    ack_ref: str | None = None
    error_code: str | None = None
    retry_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    version: int = 1

    def __post_init__(self) -> None:
        if not self.submission_id.strip():
            raise ValueError("submission_id is required")
        if not self.case_id.strip():
            raise ValueError("case_id is required")
        if not self.destination_ref.strip():
            raise ValueError("destination_ref is required")
        if not self.channel.strip():
            raise ValueError("channel is required")
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        if self.version < 1:
            raise ValueError("version must be positive")

    @classmethod
    def new(
        cls,
        *,
        submission_id: str,
        case_id: str,
        destination_ref: str,
        document_ref: str | None,
        channel: str,
        state: str = "created",
    ) -> "SubmissionRecord":
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            submission_id=submission_id,
            case_id=case_id,
            destination_ref=destination_ref,
            document_ref=document_ref,
            channel=channel,
            state=state,
            created_at=now,
            updated_at=now,
        )


class SubmissionRepository(Protocol):
    """Provider-neutral durable boundary for submission delivery facts."""

    def save(self, submission: SubmissionRecord) -> None:
        ...

    def get(self, submission_id: str) -> SubmissionRecord | None:
        ...

    def list_for_case(self, case_id: str) -> tuple[SubmissionRecord, ...]:
        ...
