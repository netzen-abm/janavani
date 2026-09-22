import pytest

from src.access.scoped_execution_policy import ScopedExecutionPolicy, ScopedExecutionRequest


def policy() -> ScopedExecutionPolicy:
    return ScopedExecutionPolicy(
        capability="citizen.document.generate",
        allowed_fields=frozenset({"issue_text"}),
        allowed_providers=frozenset({"local"}),
        allowed_processing_modes=frozenset({"deterministic"}),
        allowed_purposes=frozenset({"prepare citizen document"}),
    )


def request(**overrides) -> ScopedExecutionRequest:
    values = {
        "capability": "citizen.document.generate",
        "purpose": "prepare citizen document",
        "requested_fields": frozenset({"issue_text"}),
        "provider": "local",
        "processing_mode": "deterministic",
    }
    values.update(overrides)
    return ScopedExecutionRequest(**values)


def test_scope_within_policy_is_allowed() -> None:
    assert policy().allows(request())


@pytest.mark.parametrize(
    "overrides",
    [
        {"requested_fields": frozenset({"issue_text", "phone"})},
        {"provider": "external-provider"},
        {"processing_mode": "remote"},
        {"purpose": "unrelated purpose"},
        {"purpose": ""},
        {"capability": "other.capability"},
    ],
)
def test_scope_escape_is_denied(overrides) -> None:
    assert not policy().allows(request(**overrides))
