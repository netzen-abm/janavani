"""Implementation of the canonical Civic Case capability."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4
from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.civic_case import CaseEventType, CaseType, CivicCase
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository
from src.capabilities.civic_case_contract import CivicCaseCreateRequest, CivicCaseResult
from src.capabilities.civic_case_lifecycle import CivicCaseLifecycleMixin

CAPABILITY_ID = "JNV-CIVIC-COMPLAINT"

class CivicCaseCapability(CivicCaseLifecycleMixin):
    """Canonical Case command/query boundary shared by every access surface."""

    def __init__(self, repository: CivicCaseRepository) -> None:
        self._repository = repository

    def create(self, request: CivicCaseCreateRequest, *, identity: IdentityContext,
               source_channel: str | None = None,
               execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="create")
        subject, narrative = request.subject.strip(), request.narrative.strip()
        if not subject or not narrative:
            raise ValueError("A case requires a subject and narrative")
        decision = authorize(AuthorizationRequest(context=identity, capability=CAPABILITY_ID, action="create"))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to create a civic case")
        now = datetime.now(timezone.utc).isoformat()
        case_id = f"case-{uuid4().hex}"
        case = CivicCase(case_id=case_id, case_type=request.case_type, subject=subject, narrative=narrative,
                         created_by=identity.principal.principal_id, created_at=now, updated_at=now)
        if request.jurisdiction is not None:
            case.jurisdiction = dict(request.jurisdiction)
        case.related_organisation_id = request.related_organisation_id
        case.related_office_id = request.related_office_id
        case.related_official_id = request.related_official_id
        case.related_representative_id = request.related_representative_id
        if request.claims is not None:
            case.claims = [dict(claim) for claim in request.claims]
        case.events.append(self._event(case_id, CaseEventType.CREATED, identity, now, source_channel))
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, decision)

    def get_owned(self, case_id: str, *, identity: IdentityContext) -> CivicCase | None:
        case = self._repository.get(case_id, principal_id=identity.principal.principal_id)
        if case is None or case.created_by != identity.principal.principal_id:
            return None
        return case

    def save_owned(self, case: CivicCase, *, identity: IdentityContext,
                   execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="save")
        owned = self.get_owned(case.case_id, identity=identity)
        if owned is None or owned is not case:
            raise LookupError("Case not found")
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def add_evidence(self, case_id: str, evidence_id: str, *, identity: IdentityContext,
                     source_channel: str | None = None,
                     execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="case:add_evidence", resource_id=case_id)
        case = self._owned(case_id, identity)
        self._require(identity, "case:evidence", "case:add_evidence")
        now = datetime.now(timezone.utc).isoformat()
        case.add_evidence(evidence_id, event_id=f"event-{uuid4().hex}", occurred_at=now,
                          actor_id=identity.principal.principal_id, source_channel=source_channel)
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def add_document(self, case_id: str, document_id: str, *, identity: IdentityContext,
                     source_channel: str | None = None,
                     execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="case:add_document", resource_id=case_id)
        case = self._owned(case_id, identity)
        self._require(identity, "case:write", "case:add_document")
        now = datetime.now(timezone.utc).isoformat()
        case.add_document(document_id, event_id=f"event-{uuid4().hex}", occurred_at=now,
                          actor_id=identity.principal.principal_id, source_channel=source_channel)
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    @staticmethod
    def _validate_execution_context(execution_context, identity, *, action, resource_id=None) -> None:
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
