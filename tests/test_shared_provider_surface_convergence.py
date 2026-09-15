from __future__ import annotations

import pytest

from src.platform.composition import (
    create_consent_repository,
    create_document_review_repository_for_platform,
    create_provider_composition,
    create_submission_repository,
)
from src.storage.repositories.document_review_provider import (
    DocumentReviewProviderConfigurationError,
)


def test_platform_repository_factories_use_one_shared_provider_plan() -> None:
    composition = create_provider_composition()

    consent = create_consent_repository(provider_composition=composition)
    review = create_document_review_repository_for_platform(
        provider_composition=composition
    )
    submission = create_submission_repository(provider_composition=composition)

    assert consent is not None
    assert review is not None
    assert submission is not None


def test_document_review_fails_closed_for_unimplemented_durable_provider() -> None:
    composition = create_provider_composition().with_provider(
        "document_review", "postgres"
    )

    with pytest.raises(DocumentReviewProviderConfigurationError):
        create_document_review_repository_for_platform(
            provider_composition=composition
        )
