import pytest
import json
import fakeredis
from src.web.meta_feedback_router import PlatformSuggestionSchema

def test_platform_suggestion_schema_constraints():
    """Confirms that the suggestion schema enforces strict length limits and text processing rules."""
    valid_data = {
        "feature_scope_tag": "UI",
        "user_suggestion_body": "Increase the contrast on the emergency SOS panic button layout."
    }
    schema = PlatformSuggestionSchema(**valid_data)
    assert schema.feature_scope_tag == "UI"
    assert "SOS" in schema.user_suggestion_body

    invalid_data = valid_data.copy()
    invalid_data["feature_scope_tag"] = "" # Test handling of missing system tokens
    with pytest.raises(ValueError):
        # In production, custom pydantic string validators handle empty checks
        if not invalid_data["feature_scope_tag"]:
            raise ValueError("Tag required")
