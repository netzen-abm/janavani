"""Explicit provider selection for the canonical document-review repository."""
from __future__ import annotations

from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.document_review import (
    DocumentReviewRepository,
    InMemoryDocumentReviewRepository,
)

SUPPORTED_DOCUMENT_REVIEW_PROVIDERS = frozenset({"memory"})


class DocumentReviewProviderConfigurationError(RuntimeError):
    """Raised when the configured document-review provider is invalid."""


def create_document_review_repository(
    *, provider_composition: ProviderComposition | None = None,
) -> DocumentReviewRepository:
    """Build document-review persistence from the shared provider plan.

    PostgreSQL is intentionally not implemented here yet. A durable adapter
    requires an authoritative review lifecycle, schema, concurrency contract,
    and migration evidence before it can be selected safely.
    """
    composition = provider_composition or ProviderComposition.memory_first()
    selected = composition.provider_for("document_review")
    if selected not in SUPPORTED_DOCUMENT_REVIEW_PROVIDERS:
        raise DocumentReviewProviderConfigurationError(
            f"Unsupported document-review provider '{selected}'. Expected: memory"
        )
    return InMemoryDocumentReviewRepository()
