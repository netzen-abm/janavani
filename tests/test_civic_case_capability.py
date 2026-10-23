from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import (
    CAPABILITY_ID,
    CivicCaseCapability,
    CivicCaseCreateRequest,
)
from src.core.civic_case import CaseEventType, CaseType
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.case_content import CaseContent, InMemoryCaseContentRepository


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



def test_case_content_repository_isolates_nested_mutable_values() -> None:
    repository = InMemoryCaseContentRepository()
    claims = [{"claim": "road damage", "details": {"photos": ["photo-1"]}}]
    jurisdiction = {"district": {"name": "Example", "wards": [1, 2]}}
    content = CaseContent(
        subject="Broken road",
        narrative="A pothole is blocking the lane.",
        claims=tuple(claims),
        jurisdiction=jurisdiction,
    )

    repository.save("case-1", content, principal_id="citizen:owner")
    claims[0]["details"]["photos"].append("untrusted-mutation")
    jurisdiction["district"]["wards"].append(99)

    stored = repository.get("case-1", principal_id="citizen:owner")
    assert stored is not None
    assert stored.claims[0]["details"]["photos"] == ["photo-1"]
    assert stored.jurisdiction["district"]["wards"] == [1, 2]

    stored.claims[0]["details"]["photos"].append("read-mutation")
    stored.jurisdiction["district"]["wards"].append(100)
    reread = repository.get("case-1", principal_id="citizen:owner")
    assert reread is not None
    assert reread.claims[0]["details"]["photos"] == ["photo-1"]
    assert reread.jurisdiction["district"]["wards"] == [1, 2]


def test_case_content_repository_isolates_principals() -> None:
    repository = InMemoryCaseContentRepository()
    repository.save(
        "case-1",
        CaseContent(subject="Private", narrative="Owner-only content"),
        principal_id="citizen:owner",
    )

    assert repository.get("case-1", principal_id="citizen:other") is None
