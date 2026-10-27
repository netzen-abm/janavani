from src.services.legal_agent import JanavaniLegalAgent


def test_slm_prompt_system_instruction_anti_chat_boundaries():
    """Validate deterministic boundaries in the legal-drafting system prompt."""
    prompt = JanavaniLegalAgent.system_prompt.lower()
    assert "only" in prompt
    assert "do not answer questions" in prompt or "do not chat" in prompt
    assert "json" in prompt
    assert "legal advice" in prompt


def test_slm_prompt_regional_municipal_injection():
    """Validate the generation method injects the existing municipal profile."""
    import inspect

    method_source = inspect.getsource(JanavaniLegalAgent.draft_legal_document)
    assert "fetch_profile_by_code" in method_source
    assert "regional_profile" in method_source or "location_code" in method_source
    assert "response_format" in method_source
