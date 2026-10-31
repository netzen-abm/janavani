import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.utils.feedback_validators import ContentSanitizationEngine, OfficeFeedbackSchema


def test_experience_feedback_rating_boundaries():
    """Confirms that the validation schema flags out-of-bounds evaluation scores."""
    valid_data = {
        "office_id": "KL-TVM-01",
        "department_name": "Revenue",
        "service_rating": 4,
        "citizen_comment": "The counter officer verified the land record certificates smoothly.",
    }
    schema = OfficeFeedbackSchema(**valid_data)
    assert schema.service_rating == 4

    invalid_data = valid_data.copy()
    invalid_data["service_rating"] = 99

    with pytest.raises(ValueError):
        OfficeFeedbackSchema(**invalid_data)


def test_commentary_sanitization_and_script_filtering():
    """Confirms that markup-like tags are removed from stored commentary."""
    malicious_input = "Delayed delivery of certificates! <script>alert('hack')</script> This is bad."
    expected_output = "Delayed delivery of certificates! alert('hack') This is bad."

    sanitized_output = ContentSanitizationEngine.sanitize_commentary(malicious_input)
    assert " <script>" not in sanitized_output
    assert sanitized_output == expected_output


def test_personal_insults_are_flagged():
    """Explicit personal insults remain subject to moderation."""
    offensive_comment = "The administrative desk clerk is a total idiot and a cheat."
    assert ContentSanitizationEngine.is_safe(offensive_comment) is False


def test_corruption_allegation_is_not_rejected_by_keyword_alone():
    """A viewpoint or allegation must not be blocked solely by a keyword."""
    allegation = "I believe the officer acted corruptly and request an investigation."
    assert ContentSanitizationEngine.is_safe(allegation) is True


def test_markup_sanitization_does_not_claim_to_make_text_safe_for_html():
    """Sanitization preserves text content; output contexts still require encoding."""
    raw = "The office delayed my application <b>without explanation</b>."
    assert ContentSanitizationEngine.sanitize_commentary(raw) == (
        "The office delayed my application without explanation."
    )


def test_feedback_summary_excludes_individual_narratives(monkeypatch):
    """The summary response is aggregate-only and does not disclose comment text."""
    from src.web import feedback_router

    class FakeRecord:
        def __init__(self, rating, issue, submitted_at):
            self.rating = rating
            self.issue = issue
            self.submitted_at = submitted_at

    class FakeCapability:
        def list_for_office(self, office_id):
            assert office_id == "KL-TVM-01"
            return [
                FakeRecord(5, "PERSONAL-DRAFT-DO-NOT-EXPOSE", "2026-10-29T12:00:00Z"),
                FakeRecord(3, "CASE-IDENTIFIER-DO-NOT-EXPOSE", "2026-10-29T12:01:00Z"),
            ]

    monkeypatch.setattr(feedback_router, "_capability", lambda: FakeCapability())
    monkeypatch.setenv("JANAVANI_INTERFACE_TOKENS", "test-interface-token")
    app = FastAPI()
    app.include_router(feedback_router.router)

    response = TestClient(app).get(
        "/api/v1/feedback/summary/KL-TVM-01",
        headers={"X-Janavani-Interface-Token": "test-interface-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["aggregate_telemetry"]["total_reviews_count"] == 2
    assert body["aggregate_telemetry"]["rating_counts"] == {
        "1": 0, "2": 0, "3": 1, "4": 0, "5": 1
    }
    assert "recent_sanitized_comments" not in body
    assert "PERSONAL-DRAFT-DO-NOT-EXPOSE" not in response.text
    assert "CASE-IDENTIFIER-DO-NOT-EXPOSE" not in response.text
