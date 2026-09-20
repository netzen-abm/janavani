from src.platform.surface_case_composition import create_surface_case_composition


def test_web_and_telegram_share_the_same_case_contract():
    shared = create_surface_case_composition()

    # Access surfaces are expected to provide identities, not their own
    # Case implementations. The canonical graph is surface-neutral.
    assert shared.case_capability.__class__.__module__ == "src.capabilities.civic_case_impl"
    assert shared.evidence_capability.__class__.__module__ == "src.capabilities.evidence"
    assert shared.consent_capability.__class__.__module__ == "src.capabilities.consent"


def test_case_authorization_remains_capability_scoped():
    shared = create_surface_case_composition()

    assert shared.case_capability is not shared.civic_action_capability._case_capability
    # CivicActionCapability currently composes its own reference to the same
    # Case implementation contract; implementations must remain capability-owned
    # rather than surface-owned.
    assert type(shared.civic_action_capability._case_capability) is type(shared.case_capability)
