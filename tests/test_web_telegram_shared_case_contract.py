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


def test_vertical_slice_submission_is_fail_closed_without_delivery_configuration():
    from src.platform.surface_case_composition import create_surface_case_composition
    from src.capabilities.civic_case import CivicCaseCreateRequest
    from src.core.civic_case import CaseType

    composition = create_surface_case_composition()
    identity_context = identity()
    case = composition.case_capability.create(
        CivicCaseCreateRequest(CaseType.COMPLAINT, "Test", "Test narrative"),
        identity=identity_context,
        source_channel="webapp",
    ).case

    import pytest
    with pytest.raises(RuntimeError, match="Submission transport is not configured"):
        composition.civic_action_vertical_slice.submit(
            request=__import__("src.capabilities.submission", fromlist=["SubmissionRequest"]).SubmissionRequest(
                case_id=case.case_id,
                document_id="doc-test",
                destination_ref="office:test",
                consent_scope="office:test",
            ),
            channel_id="missing-channel",
            identity=identity_context,
            explicit_user_approval=True,
        )
