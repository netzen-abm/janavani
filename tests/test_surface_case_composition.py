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
    from src.platform.surface_case_composition import _runtime_dependency

    existing = object()
    graph = {"repository": existing}

    def must_not_run():
        raise AssertionError("cached dependency factory must not be evaluated")

    assert _runtime_dependency(graph, "repository", must_not_run) is existing
    assert graph == {"repository": existing}


def test_runtime_dependency_creates_missing_dependency_once():
    from src.platform.surface_case_composition import _runtime_dependency

    graph = {}
    created = object()
    calls = []

    def factory():
        calls.append(True)
        return created

    assert _runtime_dependency(graph, "repository", factory) is created
    assert _runtime_dependency(graph, "repository", factory) is created
    assert calls == [True]
