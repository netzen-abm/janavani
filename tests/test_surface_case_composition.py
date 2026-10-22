from src.platform.surface_case_composition import create_surface_case_composition


def test_surface_case_composition_uses_shared_capability_graph():
    composition = create_surface_case_composition()

    assert composition.case_capability is not None
    assert composition.evidence_capability is not None
    assert composition.authority_capability is not None
    assert composition.consent_capability is not None
    assert composition.civic_action_capability is not None

    # Evidence and consent must point at the same canonical Case capability.
    assert composition.evidence_capability._cases is composition.case_capability
    assert composition.consent_capability._cases is composition.case_capability
    assert composition.civic_action_capability._case_capability is composition.case_capability


def test_runtime_dependency_does_not_evaluate_cached_factory():
    from src.platform.surface_repository_graph import _runtime_dependency

    existing = object()
    graph = {"repository": existing}

    def must_not_run():
        raise AssertionError("cached dependency factory must not be evaluated")

    assert _runtime_dependency(graph, "repository", must_not_run) is existing
    assert graph == {"repository": existing}


def test_runtime_dependency_creates_missing_dependency_once():
    from src.platform.surface_repository_graph import _runtime_dependency

    graph = {}
    created = object()
    calls = []

    def factory():
        calls.append(True)
        return created

    assert _runtime_dependency(graph, "repository", factory) is created
    assert _runtime_dependency(graph, "repository", factory) is created
    assert calls == [True]



def test_production_requires_explicit_case_content_repository(monkeypatch):
    import pytest

    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")

    with pytest.raises(ValueError, match="explicitly configured CaseContentRepository"):
        create_surface_case_composition()


def test_production_rejects_in_memory_case_content_repository(monkeypatch):
    import pytest

    from src.storage.repositories.case_content import InMemoryCaseContentRepository

    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")

    with pytest.raises(ValueError, match="not permitted in production"):
        create_surface_case_composition(
            case_content_repository=InMemoryCaseContentRepository()
        )


def test_production_allows_explicit_transient_content_policy(monkeypatch):
    from src.storage.repositories.case_content import TransientCaseContentRepository

    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")
    monkeypatch.setenv("JANAVANI_CASE_CONTENT_POLICY", "transient")

    composition = create_surface_case_composition(
        case_content_repository=TransientCaseContentRepository(ttl_seconds=60, max_entries=5)
    )
    assert composition.case_capability is not None


def test_transient_case_content_expires_and_is_principal_scoped(monkeypatch):
    import src.storage.repositories.case_content as content_module
    from src.storage.repositories.case_content import CaseContent, TransientCaseContentRepository

    now = [100.0]
    monkeypatch.setattr(content_module, "monotonic", lambda: now[0])
    repository = TransientCaseContentRepository(ttl_seconds=10, max_entries=2)
    value = CaseContent(subject="Test", narrative="synthetic only")

    repository.save("case-1", value, principal_id="principal-a")
    assert repository.get("case-1", principal_id="principal-a") == value
    assert repository.get("case-1", principal_id="principal-b") is None

    now[0] = 111.0
    assert repository.get("case-1", principal_id="principal-a") is None


def test_transient_case_content_enforces_capacity():
    from src.storage.repositories.case_content import CaseContent, TransientCaseContentRepository

    repository = TransientCaseContentRepository(ttl_seconds=60, max_entries=1)
    repository.save("case-1", CaseContent(subject="one", narrative=""), principal_id="p")
    repository.save("case-2", CaseContent(subject="two", narrative=""), principal_id="p")

    assert repository.get("case-1", principal_id="p") is None
    assert repository.get("case-2", principal_id="p") is not None



def test_postgres_case_and_consent_share_atomic_persistence(monkeypatch):
    from src.storage.provider_composition import ProviderComposition
    from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
    from src.storage.repositories.consent import InMemoryConsentRepository

    monkeypatch.setenv("JANAVANI_POSTGRES_DSN", "postgresql://test-only")
    plan = (
        ProviderComposition.memory_first()
        .with_provider("civic_case", "postgres")
        .with_provider("consent", "postgres")
    )
    composition = create_surface_case_composition(
        provider_composition=plan,
        case_repository=InMemoryCivicCaseRepository(),
        consent_repository=InMemoryConsentRepository(),
    )

    from src.storage.repositories.postgres_consent_case_atomic import PostgresConsentCaseAtomicRepository
    assert isinstance(
        composition.consent_capability._atomic_repository,
        PostgresConsentCaseAtomicRepository,
    )


def test_non_postgres_consent_does_not_create_atomic_postgres_writer():
    from src.storage.provider_composition import ProviderComposition

    composition = create_surface_case_composition(
        provider_composition=ProviderComposition.memory_first()
    )
    assert composition.consent_capability._atomic_repository is None
