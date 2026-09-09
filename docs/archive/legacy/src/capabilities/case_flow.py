"""Archived legacy case-flow implementation.

ARCHIVE NOTICE
==============
This file is retained for historical/provenance purposes only.
It is not part of the active Janavani runtime and must not be imported by
new code. Canonical case lifecycle behavior belongs to the shared
CivicCaseCapability and canonical domain model.

Archived during the repository convergence work after verification that the
active implementation was duplicated elsewhere and this module had no active
runtime consumers.
"""

# Original implementation preserved verbatim below for provenance.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.core.civic_case import CivicCase
from src.identity.context import IdentityContext
from src.storage.repositories.civic_case import CivicCaseRepository


@dataclass(frozen=True)
class CaseFlowResult:
    case: CivicCase
    event: str | None = None


def _owned(repository: CivicCaseRepository, case_id: str, identity: IdentityContext) -> CivicCase:
    case = repository.get(case_id)
    if case is None or case.created_by != identity.principal.principal_id:
        raise LookupError("Case not found")
    return case


def _allow(identity: IdentityContext, capability: str, action: str, *, high_risk: bool = False) -> None:
    decision = authorize(AuthorizationRequest(
        context=identity,
        capability=capability,
        action=action,
        risk_level="high" if high_risk else "normal",
        requires_approval=high_risk,
    ))
    if decision is AuthorizationDecision.DENY:
        raise PermissionError("Capability not authorized")
    if decision is AuthorizationDecision.REQUIRE_APPROVAL:
        raise PermissionError("Explicit approval required")


def add_consent(repository: CivicCaseRepository, case_id: str, consent_id: str, *, identity: IdentityContext) -> CaseFlowResult:
    _allow(identity, "case:write", "case:consent")
    case = _owned(repository, case_id, identity)
    if consent_id not in case.consent_refs:
        case.consent_refs.append(consent_id)
    repository.save(case)
    return CaseFlowResult(case)


def add_evidence(repository: CivicCaseRepository, case_id: str, evidence_id: str, *, identity: IdentityContext, source_channel: str | None = None) -> CaseFlowResult:
    _allow(identity, "case:evidence", "case:add_evidence")
    case = _owned(repository, case_id, identity)
    now = datetime.now(timezone.utc).isoformat()
    event = case.add_evidence(evidence_id, event_id=f"event-{uuid4().hex}", occurred_at=now, actor_id=identity.principal.principal_id, source_channel=source_channel)
    repository.save(case)
    return CaseFlowResult(case, event.event_type.value)


def start_review(repository: CivicCaseRepository, case_id: str, *, identity: IdentityContext) -> CaseFlowResult:
    _allow(identity, "case:review", "case:start_review")
    case = _owned(repository, case_id, identity)
    now = datetime.now(timezone.utc).isoformat()
    event = case.start_review(event_id=f"event-{uuid4().hex}", occurred_at=now, actor_id=identity.principal.principal_id)
    repository.save(case)
    return CaseFlowResult(case, event.event_type.value)


def approve(repository: CivicCaseRepository, case_id: str, *, identity: IdentityContext) -> CaseFlowResult:
    _allow(identity, "case:write", "case:approve")
    case = _owned(repository, case_id, identity)
    now = datetime.now(timezone.utc).isoformat()
    event = case.mark_ready(event_id=f"event-{uuid4().hex}", occurred_at=now, actor_id=identity.principal.principal_id)
    repository.save(case)
    return CaseFlowResult(case, event.event_type.value)
