from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.accountability_feedback import InMemoryAccountabilityFeedbackRepository
from src.storage.repositories.accountability_feedback_provider import (
    create_accountability_feedback_repository,
)


def test_default_accountability_feedback_provider_is_memory() -> None:
    repository = create_accountability_feedback_repository()
    assert isinstance(repository, InMemoryAccountabilityFeedbackRepository)


def test_shared_composition_selects_jsonl_provider(tmp_path) -> None:
    composition = ProviderComposition.memory_first().with_provider(
        "accountability_feedback", "jsonl"
    )

    repository = create_accountability_feedback_repository(
        composition=composition,
        path=tmp_path / "feedback.jsonl",
    )

    assert repository.__class__.__name__ == "JsonlAccountabilityFeedbackRepository"
