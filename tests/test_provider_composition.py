"""Tests for the shared provider composition boundary."""
from __future__ import annotations

import pytest

from src.storage.provider_composition import (
    PERSISTED_DOMAINS,
    ProviderComposition,
    ProviderCompositionError,
)


def test_memory_first_selects_memory_for_all_persisted_domains() -> None:
    composition = ProviderComposition.memory_first()

    assert tuple(composition.providers) == PERSISTED_DOMAINS
    assert all(
        composition.provider_for(domain) == "memory" for domain in PERSISTED_DOMAINS
    )


def test_unknown_domain_is_rejected() -> None:
    with pytest.raises(ProviderCompositionError, match="Unknown persisted domains"):
        ProviderComposition({"not_a_domain": "memory"})


def test_empty_provider_is_rejected() -> None:
    with pytest.raises(ProviderCompositionError, match="Provider cannot be empty"):
        ProviderComposition({"civic_case": ""})


def test_with_provider_returns_new_immutable_plan() -> None:
    original = ProviderComposition.memory_first()
    updated = original.with_provider("civic_case", "postgres")

    assert original.provider_for("civic_case") == "memory"
    assert updated.provider_for("civic_case") == "postgres"
    assert updated.provider_for("consent") == "memory"


def test_unknown_provider_domain_lookup_is_rejected() -> None:
    composition = ProviderComposition.memory_first()

    with pytest.raises(ProviderCompositionError, match="Unknown persisted domain"):
        composition.provider_for("not_a_domain")


def test_identity_provider_is_independent_of_case_provider() -> None:
    composition = ProviderComposition.memory_first().with_provider("civic_case", "postgres")
    assert composition.provider_for("civic_case") == "postgres"
    assert composition.provider_for("external_identity_links") == "memory"


def test_identity_provider_can_be_postgres_while_case_is_memory() -> None:
    composition = ProviderComposition.memory_first().with_provider("external_identity_links", "postgres")
    assert composition.provider_for("external_identity_links") == "postgres"
    assert composition.provider_for("civic_case") == "memory"
