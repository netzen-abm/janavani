"""Regression tests for the shared authenticated agent transport."""
import logging
from unittest.mock import MagicMock

import requests

from src.adapters.agent_client import JanavaniAgentClient


def test_missing_interface_token_fails_closed(monkeypatch):
    monkeypatch.delenv("UNSET_TEST_INTERFACE_TOKEN", raising=False)
    session = MagicMock(spec=requests.Session)
    client = JanavaniAgentClient(
        "test", "UNSET_TEST_INTERFACE_TOKEN", logging.getLogger("test"),
        http_session=session,
    )

    assert client.request_document_draft("broken road") is None
    session.post.assert_not_called()


def test_draft_request_uses_interface_token_and_payload():
    session = MagicMock(spec=requests.Session)
    response = MagicMock()
    response.json.return_value = {"tracking_id": "test-1"}
    session.post.return_value = response
    client = JanavaniAgentClient(
        "test",
        "UNSET_TEST_INTERFACE_TOKEN",
        logging.getLogger("test"),
        base_url="https://agent.example",
        interface_token="test-token",
        http_session=session,
    )

    assert client.request_document_draft("broken road") == {"tracking_id": "test-1"}
    args, kwargs = session.post.call_args
    assert args[0] == "https://agent.example/api/v1/agent/draft"
    assert kwargs["json"] == {"citizen_raw_input": "broken road"}
    assert kwargs["headers"]["X-Janavani-Interface-Token"] == "test-token"
    assert kwargs["timeout"] == (3, 30)
    response.raise_for_status.assert_called_once()


def test_request_failure_does_not_expose_exception_message(caplog):
    session = MagicMock(spec=requests.Session)
    session.post.side_effect = requests.Timeout("sensitive internal detail")
    client = JanavaniAgentClient(
        "test",
        "UNSET_TEST_INTERFACE_TOKEN",
        logging.getLogger("janavani.test"),
        base_url="https://agent.example",
        interface_token="test-token",
        http_session=session,
    )

    with caplog.at_level(logging.WARNING, logger="janavani.test"):
        assert client.request_document_draft("broken road") is None
    assert "sensitive internal detail" not in caplog.text


def test_http_status_and_json_errors_fail_closed():
    session = MagicMock(spec=requests.Session)
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("sensitive error body")
    session.post.return_value = response
    client = JanavaniAgentClient(
        "test",
        "UNSET_TEST_INTERFACE_TOKEN",
        logging.getLogger("janavani.test2"),
        base_url="https://agent.example",
        interface_token="test-token",
        http_session=session,
    )
    assert client.request_document_draft("broken road") is None
