# tests/test_smoke.py


def test_search_and_rate():
    """Verify core office search and canonical feedback calls do not crash."""
    from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
    from src.services.search_directory import search_office
    from src.storage.repositories.accountability_feedback import InMemoryAccountabilityFeedbackRepository

    out = search_office("ration", "Kochi")
    assert isinstance(out, str)

    capability = AccountabilityFeedbackCapability(InMemoryAccountabilityFeedbackRepository())
    result = capability.record(
        office_id="3",
        rating=3,
        issue="smoke test issue",
        actor_ref="smoke-test",
        source_channel="test",
    )
    assert result.feedback_id.startswith("FB-")
