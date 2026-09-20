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
