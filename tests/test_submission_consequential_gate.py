"""Focused tests for the Submission -> Consequential Operation Gate boundary."""
from __future__ import annotations

import pytest

from src.access.authorization import AuthorizationRequest
from src.access.consequential import ConsequentialDecision, ConsequentialOperationRequest, gate_consequential_operation
from src.access.consent import ConsentRequirement
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.consent import InMemoryConsentRepository


def _identity(*capabilities: str) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:submission-gate",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset(capabilities),
        ),
        request_id="submission-gate-test",
    )


def _context(identity: IdentityContext, *, key: str = "submission-gate-1") -> CapabilityExecutionContext:
    return CapabilityExecutionContext.for_capability(
        identity,
        capability_id="case:submit",
        action="case:submit",
        surface="web",
        resource_id="case-1",
        idempotency_key=key,
        side_effect_class=SideEffectClass.EXTERNAL_SIDE_EFFECT,
    )


def _request(identity: IdentityContext, context: CapabilityExecutionContext, *, approval: bool = True) -> ConsequentialOperationRequest:
    requirement = ConsentRequirement(
        subject_id=identity.principal.principal_id,
        purpose="case_submission",
        scope="email:government",
    )
    return ConsequentialOperationRequest(
        authorization=AuthorizationRequest(
            context=identity,
            capability="case:submit",
            action="case:submit",
            resource_id="case-1",
            requires_approval=True,
            execution_context=context,
        ),
        execution_context=context,
        consent_requirement=requirement,
        explicit_user_approval=approval,
    )


def _consent_repository(identity: IdentityContext) -> InMemoryConsentRepository:
    repository = InMemoryConsentRepository()
    repository.save(
        Consent(
            consent_id="consent-1",
            subject_id=identity.principal.principal_id,
            purpose="case_submission",
            scope=("email:government",),
            grant_type=ConsentGrantType.EXPLICIT,
            status=ConsentStatus.GRANTED,
            created_at="2026-09-14T00:00:00Z",
        )
    )
    return repository


def test_submission_gate_fails_closed_when_authorization_is_denied() -> None:
    identity = _identity()
    context = _context(identity)
    request = _request(identity, context)
    repository = _consent_repository(identity)

    denied_identity = IdentityContext(
        principal=Principal(
            principal_id=identity.principal.principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset(),
        ),
        request_id=identity.request_id,
    )
    denied_request = _request(denied_identity, context)

    assert gate_consequential_operation(denied_request, consent_repository=repository) is ConsequentialDecision.DENY


def test_submission_gate_requires_consent() -> None:
    identity = _identity("case:submit")
    context = _context(identity)
    request = _request(identity, context)

    assert gate_consequential_operation(request) is ConsequentialDecision.CONSENT_REQUIRED


def test_submission_gate_requires_explicit_approval() -> None:
    identity = _identity("case:submit")
    context = _context(identity)
    request = _request(identity, context, approval=False)
    repository = _consent_repository(identity)

    assert gate_consequential_operation(request, consent_repository=repository) is ConsequentialDecision.REQUIRE_APPROVAL


def test_submission_gate_allows_matching_authorization_consent_and_approval() -> None:
    identity = _identity("case:submit")
    context = _context(identity)
    request = _request(identity, context)
    repository = _consent_repository(identity)

    assert gate_consequential_operation(request, consent_repository=repository) is ConsequentialDecision.ALLOW


def test_submission_gate_rejects_execution_identity_mismatch() -> None:
    authenticated = _identity("case:submit")
    execution_identity = _identity("case:submit")
    execution_identity = IdentityContext(
        principal=Principal(
            principal_id="citizen:other",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({"case:submit"}),
        ),
        request_id="other-request",
    )
    context = _context(execution_identity)
    request = ConsequentialOperationRequest(
        authorization=AuthorizationRequest(
            context=authenticated,
            capability="case:submit",
            action="case:submit",
            resource_id="case-1",
            requires_approval=True,
            execution_context=context,
        ),
        execution_context=context,
        consent_requirement=ConsentRequirement(authenticated.principal.principal_id, "case_submission", "email:government"),
        explicit_user_approval=True,
    )
    repository = _consent_repository(authenticated)

    assert gate_consequential_operation(request, consent_repository=repository) is ConsequentialDecision.DENY


def test_submission_gate_requires_matching_idempotency_context_at_capability_boundary() -> None:
    identity = _identity("case:submit")
    context = _context(identity, key="context-key")
    from src.capabilities.submission import SubmissionCapability

    with pytest.raises(ValueError, match="idempotency key"):
        SubmissionCapability._consequential_submission_decision(
            object.__new__(SubmissionCapability),
            identity=identity,
            case_id="case-1",
            consent_scope="email:government",
            explicit_user_approval=True,
            execution_context=context,
            idempotency_key="request-key",
        )
