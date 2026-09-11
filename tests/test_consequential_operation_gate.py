from src.access.authorization import AuthorizationRequest
from src.access.consequential import (
    ConsequentialDecision,
    ConsequentialOperationRequest,
    gate_consequential_operation,
)
from src.access.consent import ConsentRequirement
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.storage.repositories.consent import InMemoryConsentRepository


CAPABILITY = "case:submit"
ACTION = "submit"


def _context(*, side_effect: SideEffectClass = SideEffectClass.EXTERNAL_SIDE_EFFECT):
    identity = IdentityContext(
        principal=Principal(
            principal_id="citizen-1",
            identity_mode=IdentityMode.AUTHENTICATED,
            interface="web",
            authentication_method=AuthenticationMethod.PASSKEY,
            capabilities=frozenset({CAPABILITY}),
        ),
        request_id="req-1",
    )
    return identity, CapabilityExecutionContext.for_capability(
        identity,
        capability_id=CAPABILITY,
        action=ACTION,
        surface="web",
        resource_id="case-1",
        idempotency_key="idem-1" if side_effect is SideEffectClass.EXTERNAL_SIDE_EFFECT else None,
        side_effect_class=side_effect,
    )


def _request(*, approval=False, consent=None, side_effect=SideEffectClass.EXTERNAL_SIDE_EFFECT):
    identity, execution = _context(side_effect=side_effect)
    return ConsequentialOperationRequest(
        authorization=AuthorizationRequest(
            context=identity,
            capability=CAPABILITY,
            action=ACTION,
            resource_id="case-1",
            requires_approval=approval,
            execution_context=execution,
        ),
        execution_context=execution,
        consent_requirement=consent,
        explicit_user_approval=approval,
    )


def test_external_side_effect_requires_explicit_approval_when_policy_requires_it():
    request = _request(approval=True)
    request = ConsequentialOperationRequest(
        authorization=AuthorizationRequest(
            context=request.authorization.context,
            capability=CAPABILITY,
            action=ACTION,
            resource_id="case-1",
            requires_approval=True,
            execution_context=request.execution_context,
        ),
        execution_context=request.execution_context,
        explicit_user_approval=False,
    )
    assert gate_consequential_operation(request) is ConsequentialDecision.REQUIRE_APPROVAL


def test_explicit_approval_allows_authorized_operation():
    request = _request(approval=True)
    request = ConsequentialOperationRequest(
        authorization=request.authorization,
        execution_context=request.execution_context,
        explicit_user_approval=True,
    )
    assert gate_consequential_operation(request) is ConsequentialDecision.ALLOW


def test_missing_consent_fails_closed():
    requirement = ConsentRequirement("citizen-1", "case_submission", "submit")
    repository = InMemoryConsentRepository()
    assert (
        gate_consequential_operation(
            _request(consent=requirement), consent_repository=repository
        )
        is ConsequentialDecision.CONSENT_REQUIRED
    )


def test_matching_consent_and_approval_allow():
    requirement = ConsentRequirement("citizen-1", "case_submission", "submit")
    repository = InMemoryConsentRepository()
    repository.save(
        Consent(
            consent_id="consent-1",
            subject_id="citizen-1",
            purpose="case_submission",
            scope=("submit",),
            grant_type=ConsentGrantType.EXPLICIT,
            status=ConsentStatus.GRANTED,
            created_at="2026-09-11T00:00:00Z",
        )
    )
    request = _request(approval=True, consent=requirement)
    request = ConsequentialOperationRequest(
        authorization=request.authorization,
        execution_context=request.execution_context,
        consent_requirement=requirement,
        explicit_user_approval=True,
    )
    assert (
        gate_consequential_operation(request, consent_repository=repository)
        is ConsequentialDecision.ALLOW
    )


def test_authorization_denial_wins_over_consent_and_approval():
    identity, execution = _context()
    request = ConsequentialOperationRequest(
        authorization=AuthorizationRequest(
            context=identity,
            capability="case:forbidden",
            action=ACTION,
            resource_id="case-1",
            requires_approval=True,
            execution_context=execution,
        ),
        execution_context=execution,
        explicit_user_approval=True,
    )
    assert gate_consequential_operation(request) is ConsequentialDecision.DENY
