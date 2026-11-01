import pytest

import conversation.session as sessions


def _draft():
    return {
        "template_id": "complaint.general",
        "issue": "The public drain is blocked.",
        "subject": "",
        "existing_draft": "",
        "jurisdiction": "",
        "requested_documents": [],
    }


def test_transient_draft_is_allow_listed_and_defensively_copied(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr(sessions, "monotonic", lambda: clock[0])
    sessions.clear_session(991101)

    value = _draft()
    sessions.set_ephemeral_civic_draft(991101, value)
    value["issue"] = "Caller mutation"
    loaded = sessions.get_ephemeral_civic_draft(991101)
    assert loaded["issue"] == "The public drain is blocked."

    loaded["issue"] = "Returned mutation"
    assert sessions.get_ephemeral_civic_draft(991101)["issue"] == "The public drain is blocked."


def test_transient_draft_rejects_unknown_fields_and_oversized_content():
    with pytest.raises(ValueError, match="Unsupported transient"):
        sessions.set_ephemeral_civic_draft(991102, {
            **_draft(),
            "phone_number": "personal data",
        })

    with pytest.raises(ValueError, match="exceeds its limit"):
        sessions.set_ephemeral_civic_draft(991103, {
            **_draft(),
            "issue": "x" * 5001,
        })

    with pytest.raises(ValueError, match="records exceed limits"):
        sessions.set_ephemeral_civic_draft(991104, {
            **_draft(),
            "requested_documents": [" "],
        })


def test_transient_draft_is_purged_after_ttl_even_without_another_message(monkeypatch):
    clock = [100.0]
    monkeypatch.setattr(sessions, "monotonic", lambda: clock[0])
    sessions.clear_session(991105)
    sessions.set_ephemeral_civic_draft(991105, _draft())

    clock[0] += 901.0
    purged = sessions.purge_expired_ephemeral_issues()
    assert purged >= 1  # Other expired process-local entries may be purged in the same sweep.
    assert sessions.get_ephemeral_civic_draft(991105) is None
    assert sessions.user_sessions[991105]["_ephemeral_civic_draft"] is None
    sessions.clear_session(991105)


def test_clearing_draft_preserves_unrelated_case_session_fields():
    sessions.clear_session(991106)
    current = sessions.get_session(991106)
    current["case_id"] = "case-still-open"
    sessions.set_ephemeral_civic_draft(991106, _draft())

    sessions.clear_ephemeral_civic_draft(991106)

    assert sessions.get_session(991106)["case_id"] == "case-still-open"
    assert sessions.get_ephemeral_civic_draft(991106) is None
