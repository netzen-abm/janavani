"""Provider- and surface-neutral Civic Case capability.

This module composes the canonical domain model, identity/authorization and
persistence contracts. Web, Telegram and future surfaces invoke this shared
capability instead of implementing case creation independently.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.civic_case import CaseEvent, CaseEventType, CaseType, CivicCase
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository


CAPABILITY_ID = "JNV-CIVIC-COMPLAINT"


@dataclass(frozen=True)
class CivicCaseCreateRequest:
    """Surface-neutral input for creating a civic complaint case."""

    case_type: CaseType
    subject: str
    narrative: str


@dataclass(frozen=True)
class CivicCaseResult:
    """Stable result returned to any access surface."""

    case: CivicCase
    authorization: AuthorizationDecision


class CivicCaseCapability:
    """Shared composition boundary for CivicCase creation."""

    def __init__(self, repository: CivicCaseRepository) -> None:
        self._repository = repository

    def create(
        self,
        request: CivicCaseCreateRequest,
        *,
        identity: IdentityContext,
        source_channel: str | None = None,
    ) -> CivicCaseResult:
        decision = authorize(
            AuthorizationRequest(
                context=identity,
                capability=CAPABILITY_ID,
                action="create",
            )
        )
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to create a civic case")

        principal_id = identity.principal.principal_id
        now = datetime.now(timezone.utc).isoformat()
        case_id = f"case-{uuid4().hex}"
        case = CivicCase(
            case_id=case_id,
            case_type=request.case_type,
            subject=request.subject.strip(),
            narrative=request.narrative.strip(),
            created_by=principal_id,
            created_at=now,
            updated_at=now,
        )
        if not case.subject or not case.narrative:
            raise ValueError("A case requires a subject and narrative")

        case.events.append(
            CaseEvent(
                event_id=f"event-{uuid4().hex}",
                case_id=case_id,
                event_type=CaseEventType.CREATED,
                occurred_at=now,
                actor_id=principal_id,
                source_channel=source_channel,
            )
        )
        self._repository.save(case)
        return CivicCaseResult(case=case, authorization=decision)
