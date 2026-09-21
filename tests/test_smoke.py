# tests/test_smoke.py

def test_authority_lookup_and_feedback() -> None:
    """Verify canonical authority lookup and feedback capabilities remain usable."""
    from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
    from src.services.authority_service import find_authorities
    from src.storage.repositories.accountability_feedback import (
        InMemoryAccountabilityFeedbackRepository,
    )
    from src.storage.repositories.authority import InMemoryAuthorityRepository
    from src.core.authority import AuthorityRecord

    repository = InMemoryAuthorityRepository()
    repository.save(
        AuthorityRecord(
            authority_id="3",
            name="Kochi Ration Office",
            authority_type="ration",
            jurisdiction={"city": "Kochi"},
        )
    )

    authorities = find_authorities("ration", "Kochi", repository=repository)
    assert authorities[0].authority_id == "3"

    capability = AccountabilityFeedbackCapability(InMemoryAccountabilityFeedbackRepository())
    result = capability.record(
        office_id="3",
        rating=3,
        issue="smoke test issue",
        actor_ref="smoke-test",
        source_channel="test",
    )
    assert result.feedback_id.startswith("FB-")
