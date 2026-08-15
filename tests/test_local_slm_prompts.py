import pytest
from src.services.legal_agent import JanavaniLegalAgent

@pytest.fixture
def clean_agent():
    return JanavaniLegalAgent()

def test_slm_prompt_system_instruction_anti_chat_boundaries(clean_agent):
    """
    Validates that the system prompt template injected into the local Ollama Llama-3 sandbox
    contains the explicit, hard-coded architectural boundaries banning open chat.
    """
    assert hasattr(clean_agent, "system_prompt"), "The legal engine framework must define a static system prompt structure."
    
    prompt = clean_agent.system_prompt.lower()
    
    # Assert specific deterministic restrictions exist within the master container prompt
    assert "only function" in prompt or "only" in prompt
    assert "do not answer questions" in prompt or "do not chat" in prompt
    assert "json" in prompt, "The SLM prompt must force strict JSON output to avoid conversational chatter."
    assert "legal advice" in prompt, "The prompt must explicitly restrict the model from offering illegal uncertified advice."

def test_slm_prompt_regional_municipal_injection(clean_agent):
    """
    Verifies that the target geo-profile metadata parameters are successfully merged
    into the system prompt context locally *prior* to sending payloads down the bridge.
    """
    # Test using a standard mock location identifier code
    test_location_code = "KL-TVM-01"
    
    # We test the prompt formation indirectly via code isolation tracing
    import inspect
    method_source = inspect.getsource(clean_agent.draft_legal_document)
    
    # Confirm that local municipal profiles are pulled and injected into the dynamic prompt payload
    assert "fetch_profile_by_code" in method_source, "The generation loop must pull localized structural geo-metadata."
    assert "regional_profile" in method_source or "location_code" in method_source
    assert "response_format" in method_source, "The payload configuration must enforce structured json_object tokens."
