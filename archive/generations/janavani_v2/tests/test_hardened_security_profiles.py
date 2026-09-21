import pytest
import fakeredis
from src.web.feedback_router import HardenedFeedbackSchema

def test_hardened_feedback_token_structural_boundaries():
    """Confirms that the rating schema requires a valid platform validation token to be processed."""
    input_data = {
        "office_id": "KL-TVM-01",
        "department_name": "Revenue",
        "service_rating": 5,
        "citizen_comment": "The documentation process ran smoothly without administrative bottlenecks.",
        "zk_action_token_id": "verifiable-uuid-token-string-1234"
    }
    
    validated_schema = HardenedFeedbackSchema(**input_data)
    assert validated_schema.zk_action_token_id == "verifiable-uuid-token-string-1234"

    # Verify that an out-of-bounds evaluation score is caught by validation rules
    invalid_data = input_data.copy()
    invalid_data["service_rating"] = 42
    with pytest.raises(ValueError):
        HardenedFeedbackSchema(**invalid_data)
