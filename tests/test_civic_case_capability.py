import pytest

from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case_content import CaseContentReadinessConflictError
from src.capabilities.civic_case import (
    CAPABILITY_ID,
    CivicCaseCapability,
    CivicCaseCreateRequest,
)
from src.core.civic_case import CaseEventType, CaseType
from src.core.case_types import CaseStatus
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def _identity(*capabilities: str) -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:test",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset(capabilities),
        ),
        request_id="request-test",
    )


def test_shared_capability_creates_case_and_initial_event() -> None:
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)

    result = capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Broken streetlight",
            narrative="The streetlight has not worked for three nights.",
        ),
        identity=_identity(CAPABILITY_ID),
        source_channel="telegram",
    )

    assert result.authorization is AuthorizationDecision.ALLOW
    assert result.case.created_by == "citizen:test"
    assert result.case.events[0].event_type is CaseEventType.CREATED
    assert result.case.events[0].actor_id == "citizen:test"
    assert result.case.events[0].source_channel == "telegram"
    stored = repository.get(result.case.case_id)
    assert stored is not result.case
    assert stored.case_id == result.case.case_id
    assert stored.subject == CaseType.COMPLAINT.value
    assert stored.narrative == ""


def test_shared_capability_denies_without_capability() -> None:
    capability = CivicCaseCapability(InMemoryCivicCaseRepository())

    try:
        capability.create(
            CivicCaseCreateRequest(
                case_type=CaseType.COMPLAINT,
                subject="Broken road",
                narrative="A pothole is blocking the lane.",
            ),
            identity=_identity(),
        )
    except PermissionError:
        pass
    else:
        raise AssertionError("Expected capability authorization to deny creation")


def test_execution_envelope_is_validated_at_case_boundary() -> None:
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)
    identity = _identity(CAPABILITY_ID)
    context = CapabilityExecutionContext.for_capability(
        identity,
        capability_id=CAPABILITY_ID,
        action="create",
        surface="telegram",
    )

    result = capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Execution envelope",
            narrative="The case creation carries a provider-neutral execution context.",
        ),
        identity=identity,
        source_channel="telegram",
        execution_context=context,
    )

    assert result.case.created_by == identity.principal.principal_id


def test_execution_envelope_rejects_wrong_capability() -> None:
    capability = CivicCaseCapability(InMemoryCivicCaseRepository())
    identity = _identity(CAPABILITY_ID)
    context = CapabilityExecutionContext.for_capability(
        identity,
        capability_id="wrong:capability",
        action="create",
        surface="webapp",
    )

    try:
        capability.create(
            CivicCaseCreateRequest(
                case_type=CaseType.COMPLAINT,
                subject="Wrong envelope",
                narrative="This context must not cross capability boundaries.",
            ),
            identity=identity,
            execution_context=context,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected execution capability mismatch to be rejected")



def test_save_owned_rejects_reviewed_subject_and_narrative_before_persisting_case() -> None:
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)
    identity = _identity(CAPABILITY_ID, "case:review")
    created = capability.create(
        CivicCaseCreateRequest(CaseType.COMPLAINT, "Original subject", "Original narrative."),
        identity=identity,
    )
    capability.start_review(created.case.case_id, identity=identity)
    reviewed = capability.get_owned(created.case.case_id, identity=identity)
    assert reviewed is not None
    before = repository.get(created.case.case_id)
    reviewed.subject = "Tampered subject"
    reviewed.narrative = "Tampered narrative"
    with pytest.raises(CaseContentReadinessConflictError):
        capability.save_owned(reviewed, identity=identity)
    after = repository.get(created.case.case_id)
    assert after.subject == before.subject and after.narrative == before.narrative
    assert after.status is before.status



def test_save_owned_rejects_status_change_without_new_domain_event() -> None:
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)
    identity = _identity(CAPABILITY_ID, "case:review")
    created = capability.create(
        CivicCaseCreateRequest(CaseType.COMPLAINT, "Status invariant", "Original narrative."),
        identity=identity,
    )
    capability.start_review(created.case.case_id, identity=identity)
    reviewed = capability.get_owned(created.case.case_id, identity=identity)
    assert reviewed is not None
    before = repository.get(created.case.case_id)
    reviewed.status = CaseStatus.READY
    with pytest.raises(CaseContentReadinessConflictError):
        capability.save_owned(reviewed, identity=identity)
    after = repository.get(created.case.case_id)
    assert after.status is before.status
    assert after.events == before.events
