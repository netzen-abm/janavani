# Archived from tests/test_local_slm_prompts.py on 2026-09-01.
# Reason: the tests describe an older local-Ollama/SLM prompt architecture that
# is not the current provider-neutral AI capability contract. The active legal
# agent is OpenRouter-configurable with deterministic fallback behavior.

# Original source is preserved here for historical design reference.

import pytest
from src.services.legal_agent import JanavaniLegalAgent

@pytest.fixture
def clean_agent():
    return JanavaniLegalAgent()

def test_slm_prompt_system_instruction_anti_chat_boundaries(clean_agent):
    assert hasattr(clean_agent, "system_prompt")

def test_slm_prompt_regional_municipal_injection(clean_agent):
    import inspect
    method_source = inspect.getsource(clean_agent.draft_legal_document)
    assert "fetch_profile_by_code" in method_source
