"""Canonical submission persistence value object and repository contract."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


SUBMISSION_STATES = frozenset({
    "created",
    "submitting",
    "unknown",
    "submitted",
    "acknowledged",
    "failed",
})
RECOVERABLE_SUBMISSION_STATE = "submitting"


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
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        if not self.submission_id.strip():
            raise ValueError("submission_id is required")
        if not self.case_id.strip():
            raise ValueError("case_id is required")
        if not self.destination_ref.strip():
            raise ValueError("destination_ref is required")
        if not self.channel.strip():
            raise ValueError("channel is required")
        if self.state not in SUBMISSION_STATES:
            raise ValueError(f"Unsupported submission state: {self.state}")
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        if self.version < 1:
            raise ValueError("version must be positive")
        if self.idempotency_key is not None and not self.idempotency_key.strip():
            raise ValueError("idempotency_key must be non-empty when supplied")

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
        idempotency_key: str | None = None,
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
            idempotency_key=idempotency_key or submission_id,
        )


class SubmissionRepository(Protocol):
    """Provider-neutral durable boundary for submission delivery facts."""

    def save(self, submission: SubmissionRecord) -> None:
        ...

    def get(self, submission_id: str) -> SubmissionRecord | None:
        ...

    def get_by_idempotency_key(self, idempotency_key: str) -> SubmissionRecord | None:
        ...

    def create_idempotent(self, submission: SubmissionRecord) -> tuple[SubmissionRecord, bool]:
        """Atomically reserve a submission key; bool is True for an identical replay."""
        ...

    def update_if_version(self, submission: SubmissionRecord, *, expected_version: int) -> None:
        """Apply one state mutation only if the persisted version is unchanged."""
        ...

    def list_for_case(self, case_id: str) -> tuple[SubmissionRecord, ...]:
        ...

    def list_recoverable(self) -> tuple[SubmissionRecord, ...]:
        """Return in-flight submissions requiring restart reconciliation."""
        ...
