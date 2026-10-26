"""Provider-backed repository graph for independently hosted Janavani surfaces.

This module owns repository/provider selection and reuse. Capability orchestration
stays in surface_case_composition.py; surface-specific narrative storage is injected
by the caller because it has a separate privacy and retention contract.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.identity.linking import ExternalIdentityLinkRepository
from src.platform.composition import (
    create_authority_repository,
    create_case_repository,
    create_consent_repository,
    create_evidence_repository,
    create_identity_link_repository,
    create_provider_composition,
)
from src.platform.composition_capabilities import create_document_review_repository_for_platform
from src.storage.artifact_blob_factory import create_artifact_blob_store
from src.storage.repositories.artifact_provider import create_document_artifact_repository

_PROVIDER_RUNTIME_GRAPHS: dict[int, tuple[object, dict[str, object]]] = {}


def _provider_runtime_graph(provider_composition: object) -> dict[str, object]:
    """Reuse one set of provider-backed repositories per composition identity."""
    key = id(provider_composition)
    cached = _PROVIDER_RUNTIME_GRAPHS.get(key)
    if cached is not None and cached[0] is provider_composition:
        return cached[1]
    graph: dict[str, object] = {}
    _PROVIDER_RUNTIME_GRAPHS[key] = (provider_composition, graph)
    return graph


def _runtime_dependency(graph: dict[str, object], key: str, factory):
    """Create a dependency only on cache miss."""
    if key not in graph:
        graph[key] = factory()
    return graph[key]


@dataclass(frozen=True)
class SurfaceRepositoryGraph:
    """Provider-selected persistence dependencies shared by surface composition."""

    provider_composition: object
    case_repository: object
    authority_repository: object
    evidence_repository: object
    consent_repository: object
    identity_link_repository: ExternalIdentityLinkRepository
    artifact_repository: object
    blob_store: object
    document_review_repository: object


def create_surface_repository_graph(
    *,
    provider_composition=None,
    case_repository=None,
    authority_repository=None,
    evidence_repository=None,
    consent_repository=None,
    identity_link_repository: ExternalIdentityLinkRepository | None = None,
    artifact_repository=None,
    blob_store=None,
    document_review_repository=None,
) -> SurfaceRepositoryGraph:
    """Resolve explicit overrides or reuse dependencies from one provider graph."""
    provider_composition = provider_composition or create_provider_composition()
    graph = _provider_runtime_graph(provider_composition)

    def resolve(explicit, key, factory):
        return explicit if explicit is not None else _runtime_dependency(graph, key, factory)

    return SurfaceRepositoryGraph(
        provider_composition=provider_composition,
        case_repository=resolve(
            case_repository, "civic_case",
            lambda: create_case_repository(provider_composition=provider_composition),
        ),
        authority_repository=resolve(
            authority_repository, "authority",
            lambda: create_authority_repository(provider_composition=provider_composition),
        ),
        evidence_repository=resolve(
            evidence_repository, "evidence",
            lambda: create_evidence_repository(provider_composition=provider_composition),
        ),
        consent_repository=resolve(
            consent_repository, "consent",
            lambda: create_consent_repository(provider_composition=provider_composition),
        ),
        identity_link_repository=resolve(
            identity_link_repository, "external_identity_links",
            lambda: create_identity_link_repository(provider_composition=provider_composition),
        ),
        artifact_repository=resolve(
            artifact_repository, "document_artifacts", create_document_artifact_repository,
        ),
        blob_store=resolve(blob_store, "artifact_blob", create_artifact_blob_store),
        document_review_repository=resolve(
            document_review_repository, "document_review",
            lambda: create_document_review_repository_for_platform(provider_composition=provider_composition),
        ),
    )
