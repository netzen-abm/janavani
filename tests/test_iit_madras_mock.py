import pytest
from unittest.mock import patch, MagicMock
from src.services.legal_agent import JanavaniLegalAgent

@pytest.fixture
def mock_legal_agent():
    """Provides an initialized instance of the Janavani legal engine layer."""
    return JanavaniLegalAgent()

def test_iit_madras_malayalam_to_english_translation_mock(mock_legal_agent):
    """
    Verifies that the legal engine correctly routes vernacular input parameters
    to the IIT Madras AI4Bharat processing model endpoint.
    """
    mock_malayalam_input = "എന്റെ പ്രദേശത്തെ റോഡുകൾ തകർന്നിരിക്കുന്നു" # "The roads in my area are broken"
    mock_expected_english = "The roads in my local neighborhood area are severely broken and damaged"

    # Mock the outbound HTTP POST call to Hugging Face's inference server layout
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": mock_expected_english}
        mock_post.return_value = mock_response

        # Execute translation pipeline loop inside sandbox parameters
        translated_result = mock_legal_agent.translate_input_if_needed(
            text=mock_malayalam_input, 
            target_lang="en"
        )

        # Assert correct output matching expected english strings
        assert translated_result == mock_expected_english
        mock_post.assert_called_once()
        
        # Verify headers used private authentication parameters securely
        called_headers = mock_post.call_args[1]["headers"]
        assert "Bearer" in called_headers["Authorization"]

def test_iit_madras_translation_layer_fault_fallback(mock_legal_agent):
    """
    Guarantees that if the Hugging Face AI4Bharat endpoint drops or fails,
    the application falls back to processing the raw text without crashing.
    """
    mock_malayalam_input = "എന്റെ പ്രദേശത്തെ റോഡുകൾ തകർന്നിരിക്കുന്നു"

    with patch("requests.post") as mock_post:
        # Simulate a 503 Service Unavailable infrastructure blackout crash status code
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response

        # Execute call pipeline
        translated_result = mock_legal_agent.translate_input_if_needed(mock_malayalam_input)

        # Assert zero crash propagation: system safely falls back to native text string format
        assert translated_result == mock_malayalam_input
