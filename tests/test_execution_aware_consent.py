import pytest

from src.access.consent import ConsentRequiredError, ConsentRequirement
from src.access.execution_consent import ExecutionConsentRequirement, require_execution_consent
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.storage.repositories.consent import InMemoryConsentRepository


def _context(principal_id: str = "citizen-1"):
    identity = IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            interface="web",
            authentication_method=AuthenticationMethod.PASSKEY,
            capabilities=frozenset({"case:submit"}),
        ),
        request_id="req-1",
    )
    return CapabilityExecutionContext.for_capability(
        identity,
        capability_id="case:submit",
        action="submit",
        surface="web",
        resource_id="case-1",
        idempotency_key="idem-1",
    )


def _requirement(subject_id: str = "citizen-1"):
    return ExecutionConsentRequirement(
        ConsentRequirement(subject_id, "case_submission", "submit")
    )


def test_execution_identity_must_match_consent_subject():
    repository = InMemoryConsentRepository()
    with pytest.raises(ConsentRequiredError):
        require_execution_consent(repository, _requirement(), _context("citizen-2"))


def test_matching_granted_consent_allows_execution():
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
    require_execution_consent(repository, _requirement(), _context())


def test_missing_consent_fails_closed():
    repository = InMemoryConsentRepository()
    with pytest.raises(ConsentRequiredError):
        require_execution_consent(repository, _requirement(), _context())
