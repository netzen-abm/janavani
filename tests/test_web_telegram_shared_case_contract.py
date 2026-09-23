from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case import CAPABILITY_ID, CivicCaseCapability, CivicCaseCreateRequest
from src.commands.shared_case_capability import create_case_from_telegram
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def identity(principal_id: str = "citizen:contract-test") -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id=principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )


def test_web_and_telegram_use_the_same_case_capability_contract() -> None:
    repository = InMemoryCivicCaseRepository()
    context = identity()
    capability = CivicCaseCapability(repository)

    web_case = capability.create(
        CivicCaseCreateRequest(
            CaseType.COMPLAINT,
            "Broken streetlight",
            "The light has been off for three nights.",
        ),
        identity=context,
        source_channel="webapp",
    ).case
    telegram_case = create_case_from_telegram(
        repository,
        identity=context,
        subject="Garbage not collected",
        narrative="Waste has remained uncollected for five days.",
        case_capability=capability,
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
    other = identity("citizen:other")
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



def test_web_and_telegram_expose_the_same_vertical_slice_contract():
    from src.platform.surface_case_composition import create_surface_case_composition
    from src.capabilities.civic_action_vertical_slice import CivicActionVerticalSlice

    web = create_surface_case_composition()
    telegram = create_surface_case_composition()

    assert isinstance(web.civic_action_vertical_slice, CivicActionVerticalSlice)
    assert isinstance(telegram.civic_action_vertical_slice, CivicActionVerticalSlice)
    assert web.civic_action_vertical_slice is not telegram.civic_action_vertical_slice


def test_vertical_slice_default_transport_is_fail_closed():
    from src.platform.surface_case_composition import FailClosedSubmissionTransport
    import pytest

    with pytest.raises(RuntimeError, match="Submission transport is not configured"):
        FailClosedSubmissionTransport().send(
            case=object(), document_id="doc-test", destination_ref="office:test"
        )

def test_web_composition_delegates_to_surface_neutral_graph() -> None:
    from src.web.composition import create_web_civic_action_composition

    web = create_web_civic_action_composition()
    telegram = create_surface_case_composition()

    assert type(web) is type(telegram)
    assert type(web.case_capability) is type(telegram.case_capability)
    assert type(web.civic_action_vertical_slice) is type(telegram.civic_action_vertical_slice)
\n