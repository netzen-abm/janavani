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
        return self.transition(case_id, action="case:start_review", identity=identity)

    def approve(self, case_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        return self.transition(case_id, action="case:mark_ready", identity=identity)

    def add_consent(self, case_id: str, consent_id: str, *, identity: IdentityContext) -> CivicCaseResult:
        case = self._owned(case_id, identity)
        self._require(identity, "case:write", "case:consent")
        if consent_id not in case.consent_refs:
            case.consent_refs.append(consent_id)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def transition(self, case_id: str, *, action: str, identity: IdentityContext,
                   source_channel: str | None = None,
                   source_ref: str | None = None,
                   notes: str | None = None) -> CivicCaseResult:
        """Execute an allowed lifecycle command with shared auth and persistence."""
        transitions = {
            "case:start_review": ("case:review", CivicCase.start_review, False),
            "case:mark_ready": ("case:write", CivicCase.mark_ready, False),
            "case:begin_submission": ("case:submit", CivicCase.begin_submission, False),
            "case:queue_submission": ("case:submit", CivicCase.queue_submission, False),
            "case:submit": ("case:submit", CivicCase.submit, True),
            "case:acknowledge": ("case:write", CivicCase.acknowledge, False),
        }
        if action not in transitions:
            raise ValueError(f"Unsupported civic case transition: {action}")
        capability, transition_fn, high_risk = transitions[action]
        case = self._owned(case_id, identity)
        self._require(identity, capability, action, resource_id=case.case_id,
                      high_risk=high_risk)
        now = datetime.now(timezone.utc).isoformat()
        kwargs: dict[str, object] = {
            "event_id": f"event-{uuid4().hex}",
            "occurred_at": now,
            "actor_id": identity.principal.principal_id,
        }
        if action in {"case:begin_submission", "case:queue_submission", "case:submit", "case:acknowledge"}:
            kwargs["source_channel"] = source_channel
        if action == "case:acknowledge":
            kwargs["source_ref"] = source_ref
            kwargs["notes"] = notes
        event = transition_fn(case, **kwargs)
        self._repository.save(case)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def _owned(self, case_id: str, identity: IdentityContext) -> CivicCase:
        case = self.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        return case

    @staticmethod
    def _require(identity: IdentityContext, capability: str, action: str,
                 resource_id: str | None = None, high_risk: bool = False) -> None:
        decision = authorize(AuthorizationRequest(
            context=identity, capability=capability, action=action,
            resource_id=resource_id,
            risk_level="high" if high_risk else "normal",
            requires_approval=high_risk,
        ))
        if decision is AuthorizationDecision.DENY:
            raise PermissionError("Capability is not authorized")
        if decision is AuthorizationDecision.REQUIRE_APPROVAL:
            raise PermissionError("Explicit approval required")

    @staticmethod
    def _event(case_id: str, event_type: CaseEventType, identity: IdentityContext,
               occurred_at: str, source_channel: str | None):
        from src.core.civic_case import CaseEvent
        return CaseEvent(event_id=f"event-{uuid4().hex}", case_id=case_id,
                         event_type=event_type, occurred_at=occurred_at,
                         actor_id=identity.principal.principal_id,
                         source_channel=source_channel)
