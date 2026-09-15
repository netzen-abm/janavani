import pytest

from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
from src.storage.repositories.accountability_feedback import InMemoryAccountabilityFeedbackRepository


def make_capability():
    return AccountabilityFeedbackCapability(InMemoryAccountabilityFeedbackRepository())


def test_submit_creates_canonical_feedback():
    feedback = make_capability().submit(
        office_id="KL-TVM-01",
        rating=4,
        issue="The certificate service was completed smoothly.",
        actor_ref="citizen:anonymous",
        source_channel="telegram",
    )

    assert feedback.feedback_id.startswith("FB-")
    assert feedback.office_id == "KL-TVM-01"
    assert feedback.rating == 4
    assert feedback.source_channel == "telegram"


def test_rating_bounds_are_enforced():
    capability = make_capability()
    with pytest.raises(ValueError):
        capability.submit(office_id="office-1", rating=0, issue="Too slow")
    with pytest.raises(ValueError):
        capability.submit(office_id="office-1", rating=6, issue="Too slow")


def test_empty_feedback_is_rejected():
    with pytest.raises(ValueError):
        make_capability().submit(office_id="office-1", rating=3, issue="   ")


def test_script_markup_is_sanitized_before_persistence():
    feedback = make_capability().submit(
        office_id="office-1",
        rating=3,
        issue="Delayed <script>alert('x')</script> service",
    )
    assert "<script>" not in feedback.issue


def test_disallowed_feedback_is_rejected():
    with pytest.raises(ValueError):
        make_capability().submit(
            office_id="office-1",
            rating=2,
            issue="The officer is an idiot",
        )
