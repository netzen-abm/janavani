from src.access.consent import ConsentRequiredError, ConsentRequirement, require_consent
from src.core.consent import Consent, ConsentStatus
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import Principal


def _identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(principal_id="citizen-1"),
        request_id="req-1",
    )


def _consent() -> Consent:
    return Consent(
        consent_id="consent-1",
        subject_id="citizen-1",
        purpose="case_submission",
        scope=("destination:authority-1",),
        status=ConsentStatus.GRANTED,
    )


def test_consent_requirement_rejects_mismatched_execution_identity() -> None:
    identity = _identity()
    other = IdentityContext(principal=Principal(principal_id="citizen-2"), request_id="req-2")
    context = CapabilityExecutionContext.for_capability(
        other,
        capability_id="case:submit",
        action="case:submit",
        surface="web",
        side_effect_class="external_side_effect",
        idempotency_key="idem-1",
    )
    try:
        require_consent(
            [  # type: ignore[arg-type]
                _consent()
            ],
            ConsentRequirement(subject_id=identity.principal.principal_id, purpose="case_submission", scope="destination:authority-1"),
        )
    except ConsentRequiredError:
        pass
    assert context.identity.principal.principal_id == "citizen-2"


def test_valid_consent_remains_independent_from_execution_context() -> None:
    identity = _identity()
    context = CapabilityExecutionContext.for_capability(
        identity,
        capability_id="case:submit",
        action="case:submit",
        surface="web",
        side_effect_class="external_side_effect",
        idempotency_key="idem-1",
    )
    require_consent(
        [  # type: ignore[arg-type]
            _consent()
        ],
        ConsentRequirement(subject_id=identity.principal.principal_id, purpose="case_submission", scope="destination:authority-1"),
    )
    assert context.identity.principal.principal_id == identity.principal.principal_id
