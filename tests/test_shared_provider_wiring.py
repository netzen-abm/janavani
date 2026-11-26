"""Regression tests for shared provider configuration propagation."""
from __future__ import annotations

import pytest

import src.platform.composition_repositories as repositories
from src.platform.surface_case_composition import _get_or_create
from src.storage.provider_composition import ProviderComposition


@pytest.mark.parametrize(
    ("domain", "factory_name"),
    [
        ("consent", "create_consent_repository_for_provider"),
        ("submission", "create_submission_repository_for_provider"),
        ("authority", "create_authority_repository_for_provider"),
        ("document_artifact", "create_artifact_repository_for_provider"),
    ],
)
def test_postgres_dsn_is_propagated_to_supported_repository_factories(
    monkeypatch: pytest.MonkeyPatch,
    domain: str,
    factory_name: str,
) -> None:
    captured = {}

    def fake_factory(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(repositories, factory_name, fake_factory)
    monkeypatch.setenv("JANAVANI_POSTGRES_DSN", "postgresql://test-dsn")
    composition = ProviderComposition.memory_first().with_provider(domain, "postgres")

    if domain == "consent":
        result = repositories.create_consent_repository(provider_composition=composition)
    elif domain == "submission":
        result = repositories.create_submission_repository(provider_composition=composition)
    elif domain == "authority":
        result = repositories.create_authority_repository(provider_composition=composition)
    else:
        result = repositories.create_document_artifact_repository_for_platform(
            provider_composition=composition
        )

    assert result is not None
    assert captured == {"provider": "postgres", "dsn": "postgresql://test-dsn"}


def test_provider_graph_factory_is_lazy_and_runs_once() -> None:
    graph = {}
    calls = []

    def factory():
        calls.append("created")
        return object()

    first = _get_or_create(graph, "repository", factory)
    second = _get_or_create(graph, "repository", factory)

    assert first is second
    assert calls == ["created"]
