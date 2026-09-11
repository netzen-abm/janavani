"""Provider-neutral operation lifecycle contract."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OperationState(str, Enum):
    REQUESTED = "requested"
    AUTHORIZED = "authorized"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OperationRecord:
    operation_id: str
    capability_id: str
    action: str
    state: OperationState
    actor_id: str
    correlation_id: str | None = None
    idempotency_key: str | None = None
    error_code: str | None = None
    result_ref: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        for name, value in (("operation_id", self.operation_id), ("capability_id", self.capability_id), ("action", self.action), ("actor_id", self.actor_id)):
            if not value.strip():
                raise ValueError(f"{name} must not be blank")
        if self.state is OperationState.FAILED and not self.error_code:
            raise ValueError("Failed operations require an error_code")
