import pytest

from src.platform.capability_activation_policy import (
    CapabilityActivation,
    CapabilityActivationPolicy,
)


def test_missing_or_disabled_activation_is_denied():
    policy = CapabilityActivationPolicy(
        environment="production", surface="web", activations={}
    )
    assert policy.permits("case:submit") is False
    disabled = CapabilityActivation(
        capability_id="case:submit",
        maturity="production_approved",
        enabled=False,
        allowed_surfaces=frozenset({"web"}),
        allowed_environments=frozenset({"production"}),
        dependencies_verified=True,
        accountable_owner="security",
        approval_ref="approval:1",
    )
    assert CapabilityActivationPolicy(
        "production", "web", {"case:submit": disabled}
    ).permits("case:submit") is False


def test_production_requires_production_approval_and_all_gates():
    activation = CapabilityActivation(
        capability_id="case:submit",
        maturity="integration_verified",
        enabled=True,
        allowed_surfaces=frozenset({"web"}),
        allowed_environments=frozenset({"production"}),
        dependencies_verified=True,
        accountable_owner="security",
        approval_ref="approval:1",
    )
    policy = CapabilityActivationPolicy(
        "production", "web", {"case:submit": activation}
    )
    assert policy.permits("case:submit") is False


def test_nonproduction_activation_requires_verified_dependencies_and_exact_scope():
    activation = CapabilityActivation(
        capability_id="case:submit",
        maturity="integration_verified",
        enabled=True,
        allowed_surfaces=frozenset({"internal"}),
        allowed_environments=frozenset({"test"}),
        dependencies_verified=True,
        accountable_owner="security",
        approval_ref="approval:1",
    )
    policy = CapabilityActivationPolicy(
        "test", "internal", {"case:submit": activation}
    )
    assert policy.permits("case:submit") is True
    assert CapabilityActivationPolicy(
        "test", "web", {"case:submit": activation}
    ).permits("case:submit") is False


def test_unknown_runtime_environments_are_rejected():
    for environment in ("prod", "production-preview", "staging"):
        with pytest.raises(ValueError, match="Unsupported runtime environment"):
            CapabilityActivationPolicy(environment, "internal", {})


def test_runtime_environment_is_normalized_before_policy_evaluation():
    activation = CapabilityActivation(
        capability_id="case:submit",
        maturity="integration_verified",
        enabled=True,
        allowed_surfaces=frozenset({"internal"}),
        allowed_environments=frozenset({"test"}),
        dependencies_verified=True,
        accountable_owner="security",
        approval_ref="approval:1",
    )
    policy = CapabilityActivationPolicy(
        " TEST ", "internal", {"case:submit": activation}
    )
    assert policy.environment == "test"
    assert policy.permits("case:submit") is True


def test_unverified_dependencies_or_missing_accountability_deny_activation():
    activation = CapabilityActivation(
        capability_id="case:submit",
        maturity="integration_verified",
        enabled=True,
        allowed_surfaces=frozenset({"internal"}),
        allowed_environments=frozenset({"test"}),
        dependencies_verified=False,
        accountable_owner=None,
        approval_ref=None,
    )
    assert CapabilityActivationPolicy(
        "test", "internal", {"case:submit": activation}
    ).permits("case:submit") is False


def test_retired_capability_cannot_activate():
    activation = CapabilityActivation(
        capability_id="case:submit",
        maturity="retired",
        enabled=True,
        allowed_surfaces=frozenset({"internal"}),
        allowed_environments=frozenset({"test"}),
        dependencies_verified=True,
        accountable_owner="security",
        approval_ref="approval:1",
    )
    assert CapabilityActivationPolicy(
        "test", "internal", {"case:submit": activation}
    ).permits("case:submit") is False


def test_invalid_activation_mapping_is_rejected():
    activation = CapabilityActivation(
        capability_id="case:submit", maturity="implemented"
    )
    with pytest.raises(ValueError, match="mapping key"):
        CapabilityActivationPolicy(
            "test", "test", {"wrong:key": activation}
        )


def test_policy_snapshots_caller_mapping_and_rejects_mutation():
    activation = CapabilityActivation(
        capability_id="case:submit",
        maturity="integration_verified",
        enabled=True,
        allowed_surfaces=frozenset({"internal"}),
        allowed_environments=frozenset({"test"}),
        dependencies_verified=True,
        accountable_owner="security",
        approval_ref="approval:1",
    )
    supplied = {"case:submit": activation}
    policy = CapabilityActivationPolicy("test", "internal", supplied)
    supplied.clear()
    assert policy.permits("case:submit") is True
    with pytest.raises(TypeError):
        policy.activations["case:submit"] = activation
