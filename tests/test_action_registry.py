from src.access.action_registry import (
    ACTION_REGISTRY,
    MutationClass,
    ResourceType,
    get_action_spec,
    require_action_spec,
    registered_actions,
)


def test_registry_contains_only_unique_capability_action_pairs() -> None:
    keys = [(item.capability_id, item.action) for item in ACTION_REGISTRY]
    assert len(keys) == len(set(keys))


def test_civic_case_submission_actions_have_distinct_capability_ownership() -> None:
    case_spec = get_action_spec("JNV-CIVIC-COMPLAINT", "case:submit")
    submission_spec = get_action_spec("case:submit", "case:submit")

    assert case_spec is not None
    assert submission_spec is not None
    assert case_spec.resource is ResourceType.CASE
    assert submission_spec.resource is ResourceType.SUBMISSION
    assert case_spec.capability_id != submission_spec.capability_id


def test_high_risk_submission_requires_consent_and_approval() -> None:
    spec = require_action_spec("case:submit", "case:submit")

    assert spec.mutation is MutationClass.EXTERNAL_SIDE_EFFECT
    assert spec.consent_required is True
    assert spec.approval_required is True
    assert spec.audit_required is True


def test_unknown_action_fails_closed() -> None:
    assert get_action_spec("case:submit", "submit") is None

    try:
        require_action_spec("case:submit", "submit")
    except ValueError as exc:
        assert "Unregistered capability action" in str(exc)
    else:
        raise AssertionError("Unregistered action must fail closed")


def test_registry_is_non_empty_and_exposes_immutable_specs() -> None:
    actions = registered_actions()

    assert actions
    assert all(item.capability_id and item.action for item in actions)
