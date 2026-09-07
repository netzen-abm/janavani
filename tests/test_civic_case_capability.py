from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import (
    CAPABILITY_ID,
    CivicCaseCapability,
    CivicCaseCreateRequest,
)
from src.core.civic_case import CaseEventType, CaseType
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
    assert repository.get(result.case.case_id) is result.case


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
