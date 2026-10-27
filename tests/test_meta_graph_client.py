"""Tests for the shared outbound Meta Graph transport."""
import logging
from unittest.mock import MagicMock

import requests

from src.adapters.meta_graph_client import send_meta_message


def test_missing_credentials_do_not_make_request():
    session = MagicMock(spec=requests.Session)
    assert not send_meta_message("object-1", None, {"text": "hello"}, session)
    session.post.assert_not_called()


def test_send_uses_configured_graph_version(monkeypatch):
    monkeypatch.setenv("META_GRAPH_API_VERSION", "v26.0")
    session = MagicMock(spec=requests.Session)
    response = MagicMock()
    session.post.return_value = response

    assert send_meta_message(
        "object-1", "token-test", {"message": {"text": "hello"}}, session
    )
    args, kwargs = session.post.call_args
    assert args[0] == "https://graph.facebook.com/v26.0/object-1/messages"
    assert kwargs["headers"]["Authorization"] == "Bearer token-test"
    assert kwargs["json"] == {"message": {"text": "hello"}}
    assert kwargs["timeout"] == (2, 5)
    response.raise_for_status.assert_called_once()


def test_graph_api_error_returns_false_without_logging_message_payload(caplog):
    session = MagicMock(spec=requests.Session)
    session.post.side_effect = requests.Timeout("private-message-content")
    with caplog.at_level(logging.WARNING):
        assert not send_meta_message(
            "object-1", "token-test", {"message": {"text": "private-message-content"}}, session
        )
    assert "private-message-content" not in caplog.text
