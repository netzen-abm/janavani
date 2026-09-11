from src.access.authorization import AuthorizationRequest
from src.access.consequential import (
    ConsequentialDecision,
    ConsequentialOperationRequest,
    gate_consequential_operation,
)
from src.access.consent import ConsentRequirement
from src.access.execution_consent import ExecutionConsentRequirement, require_execution_consent
from src.core.execution import CapabilityExecutionContext, SideEffectClass
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.consent import InMemoryConsentRepository


def _identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:submission-gate",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({"case:submit"}),
        ),
        request_id="submission-gate-test",
    )


def _context(identity: IdentityContext) -> CapabilityExecutionContext:
    return CapabilityExecutionContext.for_capability(
        identity,
        capability_id="case:submit",
        action="case:submit",
        surface="web",
        resource_id="case-1",
        idempotency_key="submission-gate-1",
        side_effect_class=SideEffectClass.EXTERNAL_SIDE_EFFECT,
    )


def test_submission_gate_requires_consent_before_approval() -> None:
    identity = _identity()
    context = _context(identity)
    requirement = ConsentRequirement(identity.principal.principal_id, "case_submission", "email:government")
    request = ConsequentialOperationRequest(
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
        explicit_user_approval=True,
    )
    assert gate_consequential_operation(request) is ConsequentialDecision.CONSENT_REQUIRED


def test_submission_gate_allows_matching_consent_and_approval() -> None:
    identity = _identity()
    context = _context(identity)
    repository = InMemoryConsentRepository()
    from src.core.consent import Consent, ConsentGrantType, ConsentStatus

    repository.save(
        Consent(
            consent_id="consent-1",
            subject_id=identity.principal.principal_id,
            purpose="case_submission",
            scope=("email:government",),
            grant_type=ConsentGrantType.EXPLICIT,
            status=ConsentStatus.GRANTED,
            created_at="2026-09-11T00:00:00Z",
        )
    )
    requirement = ConsentRequirement(identity.principal.principal_id, "case_submission", "email:government")
    request = ConsequentialOperationRequest(
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
        explicit_user_approval=True,
    )
    require_execution_consent(repository, ExecutionConsentRequirement(requirement), context)
    assert gate_consequential_operation(request, consent_repository=repository) is ConsequentialDecision.ALLOW
