"""Provider- and surface-neutral Civic Case capability."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.civic_case import CaseEventType, CaseType, CivicCase
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository

CAPABILITY_ID = "JNV-CIVIC-COMPLAINT"


@dataclass(frozen=True)
class CivicCaseCreateRequest:
    case_type: CaseType
    subject: str
    narrative: str


@dataclass(frozen=True)
class CivicCaseResult:
    case: CivicCase
    authorization: AuthorizationDecision


class CivicCaseCapability:
    """Canonical Case command/query boundary shared by every access surface."""

    def __init__(self, repository: CivicCaseRepository) -> None:
        self._repository = repository

    def create(self, request: CivicCaseCreateRequest, *, identity: IdentityContext,
               source_channel: str | None = None) -> CivicCaseResult:
        subject, narrative = request.subject.strip(), request.narrative.strip()
        if not subject or not narrative:
            raise ValueError("A case requires a subject and narrative")
        decision = authorize(AuthorizationRequest(
            context=identity, capability=CAPABILITY_ID, action="create"))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to create a civic case")
        now = datetime.now(timezone.utc).isoformat()
        case_id = f"case-{uuid4().hex}"
        case = CivicCase(case_id=case_id, case_type=request.case_type,
                         subject=subject, narrative=narrative,
                         created_by=identity.principal.principal_id,
                         created_at=now, updated_at=now)
        case.events.append(self._event(case_id, CaseEventType.CREATED, identity, now, source_channel))
        self._repository.save(case)
        return CivicCaseResult(case, decision)

    def get_owned(self, case_id: str, *, identity: IdentityContext) -> CivicCase | None:
        case = self._repository.get(case_id)
        if case is None or case.created_by != identity.principal.principal_id:
            return None
        return case

    def add_evidence(self, case_id: str, evidence_id: str, *, identity: IdentityContext,
                     source_channel: str | None = None) -> CivicCaseResult:
        case = self._owned(case_id, identity)
        self._require(identity, "case:evidence", "case:add_evidence")
        now = datetime.now(timezone.utc).isoformat()
        case.add_evidence(evidence_id, event_id=f"event-{uuid4().hex}",
                          occurred_at=now, actor_id=identity.principal.principal_id,
                          source_channel=source_channel)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def add_document(self, case_id: str, document_id: str, *, identity: IdentityContext,
                     source_channel: str | None = None) -> CivicCaseResult:
        case = self._owned(case_id, identity)
        self._require(identity, "case:write", "case:add_document")
        now = datetime.now(timezone.utc).isoformat()
        case.add_document(document_id, event_id=f"event-{uuid4().hex}",
                          occurred_at=now, actor_id=identity.principal.principal_id,
                          source_channel=source_channel)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def start_review(self, case_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        case = self._owned(case_id, identity)
        self._require(identity, "case:review", "case:start_review")
        now = datetime.now(timezone.utc).isoformat()
        case.start_review(event_id=f"event-{uuid4().hex}", occurred_at=now,
                          actor_id=identity.principal.principal_id)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def approve(self, case_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        case = self._owned(case_id, identity)
        self._require(identity, "case:write", "case:approve")
        now = datetime.now(timezone.utc).isoformat()
        case.mark_ready(event_id=f"event-{uuid4().hex}", occurred_at=now,
                        actor_id=identity.principal.principal_id)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def add_consent(self, case_id: str, consent_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        case = self._owned(case_id, identity)
        self._require(identity, "case:write", "case:consent")
        if consent_id not in case.consent_refs:
            case.consent_refs.append(consent_id)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def _owned(self, case_id: str, identity: IdentityContext) -> CivicCase:
        case = self.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        return case

    @staticmethod
    def _require(identity: IdentityContext, capability: str, action: str) -> None:
        decision = authorize(AuthorizationRequest(context=identity,
                                                  capability=capability,
                                                  action=action))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Capability is not authorized")

    @staticmethod
    def _event(case_id: str, event_type: CaseEventType, identity: IdentityContext,
               occurred_at: str, source_channel: str | None):
        from src.core.civic_case import CaseEvent
        return CaseEvent(event_id=f"event-{uuid4().hex}", case_id=case_id,
                         event_type=event_type, occurred_at=occurred_at,
                         actor_id=identity.principal.principal_id,
                         source_channel=source_channel)
