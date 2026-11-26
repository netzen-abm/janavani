"""Shared lazy repository graph cache for independent Janavani surfaces."""
from __future__ import annotations

from collections.abc import Callable

_PROVIDER_RUNTIME_GRAPHS: dict[int, tuple[object, dict[str, object]]] = {}


def provider_runtime_graph(provider_composition: object) -> dict[str, object]:
    """Return one repository graph per provider composition identity."""
    key = id(provider_composition)
    cached = _PROVIDER_RUNTIME_GRAPHS.get(key)
    if cached is not None and cached[0] is provider_composition:
        return cached[1]
    graph: dict[str, object] = {}
    _PROVIDER_RUNTIME_GRAPHS[key] = (provider_composition, graph)
    return graph


def get_or_create(
    graph: dict[str, object], key: str, factory: Callable[[], object]
) -> object:
    """Instantiate each repository adapter only once per provider graph."""
    if key not in graph:
        graph[key] = factory()
    return graph[key]
