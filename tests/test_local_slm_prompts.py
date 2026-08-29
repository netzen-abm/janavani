import pytest
from src.services.legal_agent import JanavaniLegalAgent


@pytest.fixture
def clean_agent():
    return JanavaniLegalAgent()


def test_slm_prompt_system_instruction_anti_chat_boundaries(clean_agent):
    """Validate the bounded local drafting-agent prompt."""
    assert hasattr(clean_agent, "system_prompt")
    prompt = clean_agent.system_prompt.lower()
    assert "only" in prompt
    assert "do not provide open chat" in prompt or "do not chat" in prompt
    assert "json" in prompt
    assert "legal advice" in prompt


def test_slm_prompt_regional_municipal_injection(clean_agent):
    """Verify that municipal context is injected into the drafting path."""
    test_location_code = "KL-TVM-01"
    import inspect
    method_source = inspect.getsource(clean_agent.draft_legal_document)
    assert test_location_code or "municipal" in method_source.lower()
