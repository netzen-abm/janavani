from src.platform.surface_case_composition import create_surface_case_composition


def test_web_and_telegram_consume_same_canonical_case_capability_contract():
    web = create_surface_case_composition()
    telegram = create_surface_case_composition()

    assert type(web.case_capability) is type(telegram.case_capability)
    assert type(web.evidence_capability) is type(telegram.evidence_capability)
    assert type(web.consent_capability) is type(telegram.consent_capability)
    assert type(web.civic_action_capability) is type(telegram.civic_action_capability)


def test_each_surface_graph_keeps_one_case_capability_owner():
    shared = create_surface_case_composition()

    assert shared.evidence_capability._cases is shared.case_capability
    assert shared.consent_capability._cases is shared.case_capability
    assert shared.civic_action_capability._case_capability is shared.case_capability


def test_surface_composition_does_not_hide_provider_identity_in_memory():
    composition = create_surface_case_composition()
    assert composition.identity_link_repository is not None


def test_identity_linking_is_explicitly_surface_neutral():
    from src.identity.linking import IdentityLinkRequest, IdentityLinkingService, InMemoryExternalIdentityLinkRepository
    service = IdentityLinkingService(InMemoryExternalIdentityLinkRepository())
    a = service.link_verified(IdentityLinkRequest(
        principal_id="janavani:principal-a",
        provider="telegram",
        subject="tg-a",
        authentication_method="explicit_verified_link",
    ), verified=True)
    b = service.link_verified(IdentityLinkRequest(
        principal_id="janavani:principal-a",
        provider="web",
        subject="web-a",
        authentication_method="explicit_verified_link",
    ), verified=True)
    assert a.principal_id == b.principal_id


def test_web_and_telegram_can_share_provider_graph_without_sharing_surface_objects():
    from src.platform.surface_case_composition import create_surface_case_composition
    from src.storage.repositories.civic_case import InMemoryCivicCaseRepository

    shared_cases = InMemoryCivicCaseRepository()
    web = create_surface_case_composition(case_repository=shared_cases)
    telegram = create_surface_case_composition(case_repository=shared_cases)

    assert web.case_repository is telegram.case_repository
    assert web.case_capability is not telegram.case_capability
    assert web.civic_action_capability is not telegram.civic_action_capability


def test_cross_surface_identity_creates_and_retrieves_same_case_with_ownership_isolation():
    """Web and Telegram share durable providers, not application objects."""
    from src.capabilities.civic_case import CAPABILITY_ID, CivicCaseCreateRequest
    from src.core.civic_case import CaseType
    from src.identity.context import IdentityContext
    from src.identity.principal import IdentityMode, Principal
    from src.platform.composition import create_provider_composition

    providers = create_provider_composition()
    telegram = create_surface_case_composition(provider_composition=providers)
    web = create_surface_case_composition(provider_composition=providers)

    citizen_a_telegram = IdentityContext(
        principal=Principal(
            principal_id="citizen:cross-surface-a",
            identity_mode=IdentityMode.AUTHENTICATED,
            interface="telegram",
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )
    citizen_a_web = IdentityContext(
        principal=Principal(
            principal_id="citizen:cross-surface-a",
            identity_mode=IdentityMode.AUTHENTICATED,
            interface="webapp",
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )
    citizen_b_web = IdentityContext(
        principal=Principal(
            principal_id="citizen:cross-surface-b",
            identity_mode=IdentityMode.AUTHENTICATED,
            interface="webapp",
            capabilities=frozenset({CAPABILITY_ID}),
        )
    )

    created = telegram.case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Cross-surface case",
            narrative="Created through Telegram and retrieved through WebApp.",
        ),
        identity=citizen_a_telegram,
        source_channel="telegram",
    )

    assert telegram.case_repository is web.case_repository
    assert telegram.case_capability is not web.case_capability
    assert created.case.created_by == citizen_a_telegram.principal.principal_id
    assert web.case_capability.get_owned(created.case.case_id, identity=citizen_a_web) is created.case
    assert web.case_capability.get_owned(created.case.case_id, identity=citizen_b_web) is None

    # The surface boundary must not manufacture a second identity for the same citizen.
    assert citizen_a_telegram.principal.principal_id == citizen_a_web.principal.principal_id
