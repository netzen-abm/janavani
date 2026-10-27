"""Regression tests for transient conversation-session behavior."""

from src.conversation.session import clear_session, get_session, user_sessions


def test_get_session_initializes_expected_defaults():
    clear_session("session-test-user")
    session = get_session("session-test-user")

    assert session["workflow"] == "Complaint"
    assert session["identity_mode"] == "anonymous"
    assert session["issue"] == ""
    assert session["offices"] == []
    assert session["office"]["office_id"] == ""


def test_get_session_returns_same_mutable_session():
    clear_session("session-test-user")
    first = get_session("session-test-user")
    first["issue"] = "Broken road"

    second = get_session("session-test-user")
    assert second is first
    assert second["issue"] == "Broken road"


def test_clear_session_removes_only_requested_user():
    clear_session("session-test-user")
    clear_session("session-test-user-2")
    get_session("session-test-user")["issue"] = "A"
    get_session("session-test-user-2")["issue"] = "B"

    clear_session("session-test-user")

    assert get_session("session-test-user")["issue"] == ""
    assert get_session("session-test-user-2")["issue"] == "B"
