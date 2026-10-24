"""Explicit provider selection for the canonical document-review repository."""
from __future__ import annotations

from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.document_review import (
    DocumentReviewRepository,
    InMemoryDocumentReviewRepository,
    TransientDocumentReviewRepository,
)

SUPPORTED_DOCUMENT_REVIEW_PROVIDERS = frozenset({"memory", "transient"})


class DocumentReviewProviderConfigurationError(RuntimeError):
    """Raised when the configured document-review provider is invalid."""


def require_transient_document_review(
    provider: str, repository: DocumentReviewRepository, runtime_mode: str
) -> None:
    """Require bounded in-process drafts in production until durable content is approved."""
    if runtime_mode.strip().lower() == "production" and (
        provider != "transient" or not isinstance(repository, TransientDocumentReviewRepository)
    ):
        raise ValueError(
            "Production document review requires "
            "JANAVANI_DOCUMENT_REVIEW_REPOSITORY_PROVIDER=transient; "
            "no durable citizen-content adapter has been approved"
        )


def create_document_review_repository(
    *, provider_composition: ProviderComposition | None = None,
) -> DocumentReviewRepository:
    """Build document-review persistence from the shared provider plan.

    PostgreSQL is intentionally not implemented. Production uses bounded
    transient content until a separately approved durable-content contract exists.
    """
    composition = provider_composition or ProviderComposition.memory_first()
    selected = composition.provider_for("document_review")
    if selected not in SUPPORTED_DOCUMENT_REVIEW_PROVIDERS:
        raise DocumentReviewProviderConfigurationError(
            f"Unsupported document-review provider '{selected}'. Expected: memory or transient"
        )
    if selected == "transient":
        return TransientDocumentReviewRepository()
    return InMemoryDocumentReviewRepository()
