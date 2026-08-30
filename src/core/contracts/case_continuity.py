"""Shared case lifecycle and reference-number contract."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CaseStatus(str, Enum):
    INTAKE = "intake"
    ASSESSMENT = "assessment"
    ACTION_SELECTED = "action_selected"
    DOCUMENT_READY = "document_ready"
    DELIVERED = "delivered"
    AWAITING_RESPONSE = "awaiting_response"
    FOLLOW_UP_DUE = "follow_up_due"
    ESCALATION_REVIEW = "escalation_review"
    CLOSED = "closed"


@dataclass(frozen=True)
class CaseReference:
    reference_number: str
    created_at: datetime
    status: CaseStatus


@dataclass(frozen=True)
class CaseTransition:
    reference_number: str
    from_status: CaseStatus
    to_status: CaseStatus
    occurred_at: datetime
    reason: str
