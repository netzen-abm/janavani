"""Conformance tests for the shared provider-composition boundary."""
from __future__ import annotations

import pytest

from src.storage.provider_composition import (
    PERSISTED_DOMAINS,
    ProviderComposition,
    ProviderCompositionError,
)


def test_memory_first_covers_every_persisted_domain() -> None:
    composition = ProviderComposition.memory_first()

    assert set(composition.providers) == set(PERSISTED_DOMAINS)
    for domain in PERSISTED_DOMAINS:
        assert composition.provider_for(domain) == "memory"


def test_environment_composition_is_complete_and_normalized(monkeypatch) -> None:
    monkeypatch.setenv("JANAVANI_CIVIC_CASE_REPOSITORY_PROVIDER", "  POSTGRES ")
    monkeypatch.setenv("JANAVANI_ACCOUNTABILITY_FEEDBACK_REPOSITORY_PROVIDER", " JSONL ")

    composition = ProviderComposition.from_environment()

    assert composition.provider_for("civic_case") == "postgres"
    assert composition.provider_for("accountability_feedback") == "jsonl"
    assert all(composition.provider_for(domain) for domain in PERSISTED_DOMAINS)


def test_provider_override_does_not_mutate_original_plan() -> None:
    original = ProviderComposition.memory_first()
    updated = original.with_provider("evidence", "postgres")

    assert original.provider_for("evidence") == "memory"
    assert updated.provider_for("evidence") == "postgres"


def test_unknown_domains_cannot_enter_shared_composition() -> None:
    with pytest.raises(ProviderCompositionError):
        ProviderComposition({"telegram_session": "memory"})


def test_decision_only_capabilities_are_not_persistence_domains() -> None:
    decision_only = {"follow_up", "escalation"}

    assert decision_only.isdisjoint(PERSISTED_DOMAINS)
