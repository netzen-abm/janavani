import pytest
import fakeredis
from src.services.reinforcement_loop import SovereignReinforcementEngine

@pytest.fixture
def mock_reinforcement_redis():
    engine = SovereignReinforcementEngine()
    engine.redis_client = fakeredis.FakeRedis(decode_responses=True)
    return engine

def test_legal_syntax_abstraction_and_anonymization():
    """Confirms that the text processing loop successfully drops names and case coordinates from edits."""
    user_edited_draft = "To, The District Collector Shashi Tharoor, at Thiruvananthapuram Ward 4 Gata 25. Fix the pipeline."
    expected_abstract_format = "To, The District [PROPER_NOUN_BLOCK] [PROPER_NOUN_BLOCK], at [PROPER_NOUN_BLOCK] [IDENTIFIER_TAG] [IDENTIFIER_TAG]. Fix the pipeline."
    
    abstracted_output = SovereignReinforcementEngine.abstract_legal_syntax(user_edited_draft)
    
    # Assert unique identification data blocks have been securely stripped out
    assert "Shashi" not in abstracted_output
    assert "Tharoor" not in abstracted_output
    assert "Ward 4" not in abstracted_output
    assert "Gata 25" not in abstracted_output
    assert "[IDENTIFIER_TAG]" in abstracted_output

def test_reinforcement_skips_identical_payloads(mock_reinforcement_redis):
    """Verifies that the engine drops logging events if the user made zero edits to the text."""
    duplicate_text = "Standard petition body content format."
    result = mock_reinforcement_redis.record_anonymized_correction_vector(
        original_ai_text=duplicate_text,
        user_corrected_text=duplicate_text,
        document_type="RTI"
    )
    assert result is False
