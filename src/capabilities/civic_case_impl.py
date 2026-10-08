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
from src.storage.repositories.case_content import CaseContent, CaseContentRepository, InMemoryCaseContentRepository
from src.capabilities.civic_case_contract import CivicCaseCreateRequest, CivicCaseResult
from src.capabilities.civic_case_lifecycle import CivicCaseLifecycleMixin

CAPABILITY_ID = "JNV-CIVIC-COMPLAINT"

class CivicCaseCapability(CivicCaseLifecycleMixin):
    """Canonical Case command/query boundary shared by every access surface."""

    def __init__(self, repository: CivicCaseRepository, content_repository: CaseContentRepository | None = None) -> None:
        self._repository = repository
        self._content = content_repository or InMemoryCaseContentRepository()

    @property
    def repository(self) -> CivicCaseRepository:
        """Expose the capability-owned repository for composition/test boundaries."""
        return self._repository

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
        self._content.save(case.case_id, CaseContent(
            subject=subject, narrative=narrative,
            claims=tuple(dict(claim) for claim in case.claims),
            jurisdiction=dict(case.jurisdiction),
        ), principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, decision)

    def create_shell(self, request: CivicCaseCreateRequest, *, identity: IdentityContext,
                     source_channel: str | None = None,
                     execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        """Create lifecycle metadata without persisting citizen narrative/content.

        The actual citizen content remains outside durable Janavani storage. This
        shell is intentionally insufficient for review/submission until the
        selected surface supplies the content transiently or locally.
        """
        self._validate_execution_context(execution_context, identity, action="create")
        subject = request.subject.strip()
        if not subject:
            raise ValueError("A case shell requires a non-sensitive subject/category")
        decision = authorize(AuthorizationRequest(context=identity, capability=CAPABILITY_ID, action="create"))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized to create a civic case")
        now = datetime.now(timezone.utc).isoformat()
        case_id = f"case-{uuid4().hex}"
        case = CivicCase(
            case_id=case_id,
            case_type=request.case_type,
            subject=subject,
            narrative="",
            created_by=identity.principal.principal_id,
            created_at=now,
            updated_at=now,
        )
        case.events.append(self._event(case_id, CaseEventType.CREATED, identity, now, source_channel))
        self._repository.save(case, principal_id=identity.principal.principal_id)
        return CivicCaseResult(case, decision)

    def get_owned(self, case_id: str, *, identity: IdentityContext) -> CivicCase | None:
        case = self._repository.get(case_id, principal_id=identity.principal.principal_id)
        if case is None or case.created_by != identity.principal.principal_id:
            return None
        content = self._content.get(case_id, principal_id=identity.principal.principal_id)
        if content is not None:
            # Durable Case.subject is workflow metadata (the canonical case type).
            # Citizen-authored content is reconstructed only from the separate
            # content boundary; never overwrite durable metadata with it.
            case.narrative = content.narrative
            case.claims = [dict(claim) for claim in content.claims]
            case.jurisdiction = dict(content.jurisdiction)
        return case

    def save_owned(self, case: CivicCase, *, identity: IdentityContext,
                   execution_context: CapabilityExecutionContext | None = None) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="save")
        owned = self.get_owned(case.case_id, identity=identity)
        if owned is None or owned.case_id != case.case_id:
            raise LookupError("Case not found")
        self._repository.save(case, principal_id=identity.principal.principal_id)
        self._save_content(case, identity=identity)
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
        self._save_content(case, identity=identity)
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
        self._save_content(case, identity=identity)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def _save_content(self, case: CivicCase, *, identity: IdentityContext) -> None:
        existing = self._content.get(
            case.case_id,
            principal_id=identity.principal.principal_id,
        )
        self._content.save(
            case.case_id,
            CaseContent(
                subject=existing.subject if existing is not None else case.subject,
                narrative=case.narrative,
                claims=tuple(dict(claim) for claim in case.claims),
                jurisdiction=dict(case.jurisdiction),
            ),
            principal_id=identity.principal.principal_id,
        )

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
