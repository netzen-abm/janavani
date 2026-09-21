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


def test_web_and_telegram_share_all_injected_provider_repositories():
    from src.platform.composition import create_provider_composition

    providers = create_provider_composition()
    web = create_surface_case_composition(provider_composition=providers)
    telegram = create_surface_case_composition(provider_composition=providers)

    assert web.case_repository is telegram.case_repository
    assert web.authority_repository is telegram.authority_repository
    assert web.evidence_repository is telegram.evidence_repository
    assert web.consent_repository is telegram.consent_repository
    assert web.identity_link_repository is telegram.identity_link_repository

    # Sharing durable state must never imply sharing mutable surface capability objects.
    assert web.case_capability is not telegram.case_capability
    assert web.authority_capability is not telegram.authority_capability
    assert web.evidence_capability is not telegram.evidence_capability
    assert web.consent_capability is not telegram.consent_capability
    assert web.civic_action_capability is not telegram.civic_action_capability


def test_cross_surface_case_evidence_and_consent_converge_on_shared_provider_state():
    from src.capabilities.civic_case import CAPABILITY_ID, CivicCaseCreateRequest
    from src.core.consent import Consent, ConsentGrantType, ConsentStatus
    from src.core.civic_case import CaseType
    from src.core.evidence import EvidenceObject, EvidenceSource
    from src.identity.context import IdentityContext
    from src.identity.principal import IdentityMode, Principal
    from src.platform.composition import create_provider_composition

    providers = create_provider_composition()
    telegram = create_surface_case_composition(provider_composition=providers)
    web = create_surface_case_composition(provider_composition=providers)

    citizen_a = IdentityContext(principal=Principal(
        principal_id="citizen:vertical-a", identity_mode=IdentityMode.AUTHENTICATED,
        interface="telegram", capabilities=frozenset({CAPABILITY_ID}),
    ))
    citizen_a_web = IdentityContext(principal=Principal(
        principal_id="citizen:vertical-a", identity_mode=IdentityMode.AUTHENTICATED,
        interface="webapp", capabilities=frozenset({CAPABILITY_ID}),
    ))
    citizen_b = IdentityContext(principal=Principal(
        principal_id="citizen:vertical-b", identity_mode=IdentityMode.AUTHENTICATED,
        interface="webapp", capabilities=frozenset({CAPABILITY_ID}),
    ))

    created = telegram.case_capability.create(CivicCaseCreateRequest(
        case_type=CaseType.COMPLAINT,
        subject="Shared evidence and consent",
        narrative="Cross-surface state must converge without crossing ownership.",
    ), identity=citizen_a, source_channel="telegram")
    case_id = created.case.case_id

    web.evidence_repository.save(EvidenceObject(
        evidence_id="evidence:shared-vertical",
        evidence_type="photo",
        storage_ref="local://shared-vertical",
        sha256="b" * 64,
        received_at="2026-09-21T00:00:00Z",
        provenance=(EvidenceSource(source_id="capture:shared", source_type="citizen"),),
    ))
    attached = web.evidence_capability.attach(
        case_id, "evidence:shared-vertical", identity=citizen_a_web, source_channel="webapp"
    )
    assert "evidence:shared-vertical" in attached.case.evidence_refs

    telegram_view = telegram.case_capability.get_owned(case_id, identity=citizen_a)
    assert telegram_view is not None
    assert "evidence:shared-vertical" in telegram_view.evidence_refs
    assert web.case_capability.get_owned(case_id, identity=citizen_b) is None

    web.consent_repository.save(Consent(
        consent_id="consent:shared-vertical",
        subject_id="citizen:vertical-a",
        purpose="case_submission",
        scope=("case_submission",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-21T00:01:00Z",
    ))
    consented = web.case_capability.add_consent(
        case_id, "consent:shared-vertical", identity=citizen_a_web,
    )
    assert "consent:shared-vertical" in consented.case.consent_refs
    assert "consent:shared-vertical" in telegram.case_capability.get_owned(
        case_id, identity=citizen_a
    ).consent_refs
