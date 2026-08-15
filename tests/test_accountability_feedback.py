import pytest
from src.utils.feedback_validators import ContentSanitizationEngine, OfficeFeedbackSchema

def test_experience_feedback_rating_boundaries():
    """Confirms that the validation schema flags out-of-bounds evaluation scores."""
    valid_data = {
        "office_id": "KL-TVM-01",
        "department_name": "Revenue",
        "service_rating": 4,
        "citizen_comment": "The counter officer verified the land record certificates smoothly."
    }
    schema = OfficeFeedbackSchema(**valid_data)
    assert schema.service_rating == 4

    invalid_data = valid_data.copy()
    invalid_data["service_rating"] = 99 # Pass an invalid rating score
    
    with pytest.raises(ValueError):
        OfficeFeedbackSchema(**invalid_data)

def test_commentary_sanitization_and_script_filtering():
    """Confirms that malicious code fragments are stripped from public text entries."""
    malicious_input = "Delayed delivery of certificates! <script>alert('hack')</script> This is bad."
    expected_output = "Delayed delivery of certificates! alert('hack') This is bad."
    
    sanitized_output = ContentSanitizationEngine.sanitize_commentary(malicious_input)
    assert " <script>" not in sanitized_output
    assert sanitized_output == expected_output

def test_profanity_block_interception():
    """Confirms that feedback entries containing explicit personal attacks are blocked entirely."""
    offensive_comment = "The administrative desk clerk is a total idiot and a cheat."
    
    assert ContentSanitizationEngine.is_safe(offensive_comment) is False
