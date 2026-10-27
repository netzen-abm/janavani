import pytest
from unittest.mock import MagicMock, patch

from src.services.legal_agent import JanavaniLegalAgent
from src.core.settings import ai_settings


@pytest.fixture
def mock_legal_agent(monkeypatch):
    """Provide a deterministic legal-engine instance with mock translation credentials."""
    monkeypatch.setattr(ai_settings, "HUGGINGFACE_API_KEY", "test-huggingface-key")
    return JanavaniLegalAgent()


def test_iit_madras_malayalam_to_english_translation_mock(mock_legal_agent):
    """Verify configured translation output is returned for vernacular input."""
    mock_malayalam_input = "എന്റെ പ്രദേശത്തെ റോഡുകൾ തകർന്നിരിക്കുന്നു"
    mock_expected_english = "The roads in my local neighborhood area are severely broken and damaged"

    with patch.object(mock_legal_agent._session, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": mock_expected_english}
        mock_post.return_value = mock_response

        translated_result = mock_legal_agent.translate_input_if_needed(
            text=mock_malayalam_input,
            target_lang="en",
        )

        assert translated_result == mock_expected_english
        mock_post.assert_called_once()
        called_headers = mock_post.call_args.kwargs["headers"]
        assert "Bearer" in called_headers["Authorization"]


def test_iit_madras_translation_layer_fault_fallback(mock_legal_agent):
    """Verify a translation-service failure safely returns the source text."""
    mock_malayalam_input = "എന്റെ പ്രദേശത്തെ റോഡുകൾ തകർന്നിരിക്കുന്നു"

    with patch.object(mock_legal_agent._session, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response

        translated_result = mock_legal_agent.translate_input_if_needed(mock_malayalam_input)

        assert translated_result == mock_malayalam_input
