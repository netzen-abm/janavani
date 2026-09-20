"""Civic Case lifecycle operations split from the main capability."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from src.access.authorization import AuthorizationDecision
from src.core.civic_case import CaseEventType, CivicCase

class CivicCaseLifecycleMixin:
    def start_review(self, case_id: str, *, identity: IdentityContext,
                     execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        return self.transition(case_id, action="case:start_review", identity=identity, execution_context=execution_context)

    def approve(self, case_id: str, *, identity: IdentityContext,
                execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        return self.transition(case_id, action="case:mark_ready", identity=identity, execution_context=execution_context)

    def add_consent(
        self,
        case_id: str,
        consent_id: str,
        *,
        identity: IdentityContext,
        execution_context: CapabilityExecutionContext | None = None,
    ) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="case:consent", resource_id=case_id)
        case = self._owned(case_id, identity)
        self._require(identity, "case:write", "case:consent")
        if consent_id not in case.consent_refs:
            case.consent_refs.append(consent_id)
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def transition(
        self,
        case_id: str,
        *,
        action: str,
        identity: IdentityContext,
        source_channel: str | None = None,
        source_ref: str | None = None,
        notes: str | None = None,
        execution_context: CapabilityExecutionContext | None = None,
    ) -> CivicCaseResult:
        transitions = {
            "case:start_review": ("case:review", CivicCase.start_review, False),
            "case:mark_ready": ("case:write", CivicCase.mark_ready, False),
            "case:begin_submission": ("case:submit", CivicCase.begin_submission, False),
            "case:queue_submission": ("case:submit", CivicCase.queue_submission, False),
            "case:submit": ("case:submit", CivicCase.submit, False),
            "case:acknowledge": ("case:write", CivicCase.acknowledge, False),
            "case:verify_resolution": ("case:write", CivicCase.verify_resolution, False),
            "case:reopen_resolution": ("case:write", CivicCase.reopen_after_citizen_verification, False),
        }
        if action not in transitions:
            raise ValueError(f"Unsupported civic case transition: {action}")
        capability, transition_fn, high_risk = transitions[action]
        self._validate_execution_context(execution_context, identity, action=action, resource_id=case_id)
        case = self._owned(case_id, identity)
        self._require(identity, capability, action, resource_id=case.case_id, high_risk=high_risk)
        now = datetime.now(timezone.utc).isoformat()
        kwargs: dict[str, object] = {"event_id": f"event-{uuid4().hex}", "occurred_at": now,
                                     "actor_id": identity.principal.principal_id}
        if action in {"case:begin_submission", "case:queue_submission", "case:submit", "case:acknowledge",
                      "case:verify_resolution", "case:reopen_resolution"}:
            kwargs["source_channel"] = source_channel
        if action in {"case:acknowledge", "case:verify_resolution"}:
            kwargs["source_ref"] = source_ref
            kwargs["notes"] = notes
        if action == "case:reopen_resolution":
            kwargs["notes"] = notes
        transition_fn(case, **kwargs)
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def _owned(self, case_id: str, identity: IdentityContext) -> CivicCase:
        case = self.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        return case

    @staticmethod
    def _validate_execution_context(
        execution_context: CapabilityExecutionContext | None,
        identity: IdentityContext,
        *,
        action: str,
        resource_id: str | None = None,
    ) -> None:
        """Validate an envelope when a caller supplies one; legacy callers remain compatible."""
        if execution_context is None:
            return
        if execution_context.identity.principal.principal_id != identity.principal.principal_id:
            raise PermissionError("Execution identity does not match the authenticated identity")
        if execution_context.capability_id != CAPABILITY_ID:
            raise ValueError("Execution capability does not match the Civic Case capability")
        if execution_context.action != action:
            raise ValueError("Execution action does not match the Civic Case operation")
        if resource_id is not None and execution_context.resource_id != resource_id:
            raise ValueError("Execution resource does not match the Civic Case resource")

    @staticmethod
    def _require(identity: IdentityContext, capability: str, action: str,
                 resource_id: str | None = None, high_risk: bool = False) -> None:
        decision = authorize(AuthorizationRequest(context=identity, capability=capability, action=action,
                                                  resource_id=resource_id, risk_level="high" if high_risk else "normal",
                                                  requires_approval=high_risk))
        if decision is AuthorizationDecision.DENY:
            raise PermissionError("Capability is not authorized")
        if decision is AuthorizationDecision.REQUIRE_APPROVAL:
            raise PermissionError("Explicit approval required")

    @staticmethod
    def _event(case_id: str, event_type: CaseEventType, identity: IdentityContext, occurred_at: str, source_channel: str | None):
        from src.core.civic_case import CaseEvent
        return CaseEvent(event_id=f"event-{uuid4().hex}", case_id=case_id, event_type=event_type,
                         occurred_at=occurred_at, actor_id=identity.principal.principal_id, source_channel=source_channel)
