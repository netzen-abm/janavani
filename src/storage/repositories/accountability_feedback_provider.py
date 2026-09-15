"""Provider selection for the canonical accountability feedback repository."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from src.core.accountability_feedback import AccountabilityFeedbackRepository
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.accountability_feedback import (
    InMemoryAccountabilityFeedbackRepository,
)

SUPPORTED_PROVIDERS = frozenset({"memory", "jsonl"})


class AccountabilityFeedbackProviderConfigurationError(RuntimeError):
    """Raised when the configured feedback provider is invalid."""


def create_accountability_feedback_repository(
    provider: str | None = None,
    *,
    composition: ProviderComposition | None = None,
    path: str | Path | None = None,
) -> AccountabilityFeedbackRepository:
    """Build the feedback repository from the shared provider composition."""
    selected = (
        composition.provider_for("accountability_feedback")
        if composition is not None
        else provider
        or os.getenv("JANAVANI_ACCOUNTABILITY_FEEDBACK_REPOSITORY_PROVIDER", "memory")
    ).strip().lower()

    if selected not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise AccountabilityFeedbackProviderConfigurationError(
            f"Unsupported accountability feedback provider '{selected}'. "
            f"Expected one of: {supported}"
        )

    if selected == "memory":
        return InMemoryAccountabilityFeedbackRepository()

    from src.storage.repositories.accountability_feedback_jsonl import (
        JsonlAccountabilityFeedbackRepository,
    )

    return JsonlAccountabilityFeedbackRepository(path or "database/ratings.jsonl")
