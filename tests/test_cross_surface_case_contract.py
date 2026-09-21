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
