import pytest
from src.services.legal_knowledge_guard import AirGappedKnowledgeGuardrail
from src.core.regional_lexicon import fetch_lexicon_by_language

def test_airgapped_guardrail_rejection_mechanics():
    """Confirms that the input scanner successfully catches and blocks out-of-scope chat queries."""
    allowed_civic_query = "Draft an objection petition against the new land tracking amendment bill."
    unauthorized_chat_query = "Write a python script to sort a list or tell me a joke."
    
    # Assert successful validation and context mapping for allowed queries
    allowed_evaluation = AirGappedKnowledgeGuardrail.verify_and_extract_context(allowed_civic_query)
    assert allowed_evaluation is not None
    assert allowed_evaluation["is_valid_civic_intent"] is True
    
    # Assert immediate rejection and termination for unauthorized chat inputs
    unauthorized_evaluation = AirGappedKnowledgeGuardrail.verify_and_extract_context(unauthorized_chat_query)
    assert unauthorized_evaluation is None

def test_regional_lexicon_translation_strings():
    """Verifies that the lexicon database correctly returns language-specific text blocks."""
    malayalam_assets = fetch_lexicon_by_language("Malayalam")
    assert "ഭാരതത്തിലെ ജനങ്ങളായ നാം" in malayalam_assets["preamble_anchor"]
    
    hindi_assets = fetch_lexicon_by_language("Hindi")
    assert "हम, भारत के लोग" in hindi_assets["preamble_anchor"]
