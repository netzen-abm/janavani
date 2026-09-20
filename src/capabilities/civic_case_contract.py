"""Provider- and surface-neutral Civic Case capability."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.civic_case import CaseType, CivicCase
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository

CAPABILITY_ID = "JNV-CIVIC-COMPLAINT"


@dataclass(frozen=True)
class CivicCaseCreateRequest:
    case_type: CaseType
    subject: str
    narrative: str
    jurisdiction: dict[str, object] | None = None
    related_organisation_id: str | None = None
    related_office_id: str | None = None
    related_official_id: str | None = None
    related_representative_id: str | None = None
    claims: list[dict[str, object]] | None = None


@dataclass(frozen=True)
class CivicCaseResult:
    case: CivicCase
    authorization: AuthorizationDecision


