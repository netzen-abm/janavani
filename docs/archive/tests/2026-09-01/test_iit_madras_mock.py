# Archived from tests/test_iit_madras_mock.py on 2026-09-01.
# Reason: this test targets an IIT Madras/Hugging Face translation adapter that
# is not implemented by the current provider-neutral language capability.
# Preserve it as historical design material; do not make CI pretend this
# capability is active.

# Original test source preserved for future adapter work.

import pytest
from unittest.mock import patch, MagicMock
from src.services.legal_agent import JanavaniLegalAgent
from src.core.settings import ai_settings

@pytest.fixture
def mock_legal_agent(monkeypatch):
    monkeypatch.setattr(ai_settings, "HUGGINGFACE_API_KEY", "test-huggingface-key")
    return JanavaniLegalAgent()


def test_iit_madras_malayalam_to_english_translation_mock(mock_legal_agent):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": "translated"}
        mock_post.return_value = mock_response
        assert mock_legal_agent.translate_input_if_needed("source", target_lang="en") == "translated"


def test_iit_madras_translation_layer_fault_fallback(mock_legal_agent):
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response
        assert mock_legal_agent.translate_input_if_needed("source") == "source"
