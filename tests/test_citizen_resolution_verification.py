from __future__ import annotations

import pytest

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.core.civic_case import CaseEventType, CaseStatus, CaseType
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def _identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:verification-test",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}),
        ),
        request_id="verification-request-test",
    )


def _resolved_case() -> tuple[CivicCaseCapability, IdentityContext, str]:
    identity = _identity()
    capability = CivicCaseCapability(InMemoryCivicCaseRepository())
    case = capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Streetlight repair",
            narrative="Streetlight remains broken.",
        ),
        identity=identity,
    ).case
    capability.start_review(case.case_id, identity=identity)
    capability.add_consent(case.case_id, "consent-1", identity=identity)
    capability.approve(case.case_id, identity=identity)
    capability.transition(case.case_id, action="case:begin_submission", identity=identity)
    capability.transition(case.case_id, action="case:submit", identity=identity)
    capability.transition(case.case_id, action="case:acknowledge", identity=identity, source_ref="ack-evidence-1")
    capability.transition(case.case_id, action="case:responded", identity=identity) if False else None
    case = capability.get_owned(case.case_id, identity=identity)
    case.status = CaseStatus.RESPONDED
    capability.save_owned(case, identity=identity)
    case = capability.get_owned(case.case_id, identity=identity)
    case.resolve(event_id="event-authority-resolved", occurred_at="2026-09-10T10:00:00Z", actor_id="authority:example")
    capability.save_owned(case, identity=identity)
    return capability, identity, case.case_id


def test_citizen_verification_is_distinct_from_authority_resolution() -> None:
    capability, identity, case_id = _resolved_case()
    result = capability.transition(
        case_id,
        action="case:verify_resolution",
        identity=identity,
        source_channel="web",
        source_ref="citizen-observation-1",
        notes="Citizen inspected the repair and confirms the issue is resolved.",
    )

    assert result.case.status is CaseStatus.RESOLVED
    assert result.case.citizen_verified_resolution() is True
    assert result.case.events[-1].event_type is CaseEventType.CITIZEN_VERIFIED
    assert result.case.events[-1].source_ref == "citizen-observation-1"


def test_citizen_can_reopen_an_authority_resolved_case() -> None:
    capability, identity, case_id = _resolved_case()
    result = capability.transition(
        case_id,
        action="case:reopen_resolution",
        identity=identity,
        source_channel="web",
        notes="Repair is incomplete; the original problem remains.",
    )

    assert result.case.status is CaseStatus.FOLLOW_UP
    assert result.case.events[-1].event_type is CaseEventType.CITIZEN_REOPENED


def test_citizen_verification_requires_resolved_case() -> None:
    identity = _identity()
    capability = CivicCaseCapability(InMemoryCivicCaseRepository())
    case = capability.create(
        CivicCaseCreateRequest(case_type=CaseType.COMPLAINT, subject="Issue", narrative="Still open."),
        identity=identity,
    ).case

    with pytest.raises(ValueError, match="resolved"):
        capability.transition(case.case_id, action="case:verify_resolution", identity=identity)
