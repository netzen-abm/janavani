# ARCHIVED TEST — NOT PART OF THE ACTIVE SUITE
#
# This test targets a retired translation API and the retired
# HUGGINGFACE_API_KEY setting. The active JanavaniLegalAgent now
# exposes draft_legal_document() and uses HF_TOKEN.
# The original test is preserved here for provenance.

import pytest
from unittest.mock import patch, MagicMock
from src.services.legal_agent import JanavaniLegalAgent
from src.core.settings import ai_settings


@pytest.fixture
def mock_legal_agent(monkeypatch):
    """Provide a deterministic legal-engine instance."""
    monkeypatch.setattr(
        ai_settings,
        "HUGGINGFACE_API_KEY",
        "test-huggingface-key",
    )
    return JanavaniLegalAgent()


def test_iit_madras_malayalam_to_english_translation_mock(mock_legal_agent):
    """Verify the retired translation endpoint behavior."""
    mock_input = "എന്റെ പ്രദേശത്തെ റോഡുകൾ തകർന്നിരിക്കുന്നു"
    expected = "The roads in my local neighborhood area are severely broken and damaged"

    with patch("requests.post") as mock_post:
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"generated_text": expected}
        mock_post.return_value = response

        result = mock_legal_agent.translate_input_if_needed(
            text=mock_input,
            target_lang="en",
        )

        assert result == expected
        mock_post.assert_called_once()
        headers = mock_post.call_args[1]["headers"]
        assert "Bearer" in headers["Authorization"]


def test_iit_madras_translation_layer_fault_fallback(mock_legal_agent):
    """Verify the retired translation failure fallback."""
    mock_input = "എന്റെ പ്രദേശത്തെ റോഡുകൾ തകർന്നിരിക്കുന്നു"

    with patch("requests.post") as mock_post:
        response = MagicMock()
        response.status_code = 503
        mock_post.return_value = response

        result = mock_legal_agent.translate_input_if_needed(mock_input)

        assert result == mock_input
