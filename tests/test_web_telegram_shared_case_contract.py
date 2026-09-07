from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import CAPABILITY_ID, CivicCaseCapability, CivicCaseCreateRequest
from src.commands.shared_case_capability import create_case_from_telegram
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.web.civic_case_capability_adapter import create_case_capability


def identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen:contract-test",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )


def test_web_and_telegram_use_the_same_case_capability_contract() -> None:
    repository = InMemoryCivicCaseRepository()
    context = identity()

    web_case = create_case_capability(
        repository,
        identity=context,
        case_type=CaseType.COMPLAINT,
        subject="Broken streetlight",
        narrative="The light has been off for three nights.",
    )
    telegram_case = create_case_from_telegram(
        repository,
        identity=context,
        subject="Garbage not collected",
        narrative="Waste has remained uncollected for five days.",
    )

    assert web_case.created_by == telegram_case.created_by == context.principal.principal_id
    assert web_case.events[0].source_channel == "webapp"
    assert telegram_case.events[0].source_channel == "telegram"
    assert web_case.case_type is CaseType.COMPLAINT
    assert telegram_case.case_type is CaseType.COMPLAINT


def test_cross_surface_continuation_is_owner_scoped() -> None:
    repository = InMemoryCivicCaseRepository()
    capability = CivicCaseCapability(repository)
    owner = identity()
    other = IdentityContext(
        principal=Principal(
            principal_id="citizen:other",
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )
    case = capability.create(
        CivicCaseCreateRequest(CaseType.COMPLAINT, "Road damage", "A pothole is blocking traffic."),
        identity=owner,
        source_channel="webapp",
    ).case

    assert capability.get_owned(case.case_id, identity=owner) is case
    assert capability.get_owned(case.case_id, identity=other) is None
    assert capability.create(
        CivicCaseCreateRequest(CaseType.COMPLAINT, "Water leak", "A public pipe is leaking."),
        identity=owner,
    ).authorization is AuthorizationDecision.ALLOW
