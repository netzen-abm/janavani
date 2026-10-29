import pytest

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
