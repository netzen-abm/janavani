"""Ephemeral Telegram workflow state.

Privacy invariant:
- This state is process-local only.
- It must never contain citizen names, addresses, contact details, identity
  documents, raw issue narratives, evidence bytes, or other personal/sensitive
  content.
- Citizen content is consumed from the current Telegram update when required
  and is not copied into this session store.
"""
from __future__ import annotations

from time import monotonic

user_sessions: dict[int, dict] = {}
_EPHEMERAL_TTL_SECONDS = 15 * 60


def get_session(user_id: int) -> dict:
    """Return minimal non-sensitive workflow state for a Telegram user."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "workflow": "Complaint",
            "district": "",
            "department": "",
            "offices": [],
            "office": {
                "office_id": "",
                "office_name": "",
                "office_address": "",
                "department": "",
                "district": "",
            },
            "identity_mode": "anonymous",
            "case_id": "",
            "format": "",
            "document_id": "",
            "_ephemeral_issue": None,
            "_ephemeral_issue_expires": 0.0,
        }
    return user_sessions[user_id]


def clear_session(user_id: int) -> None:
    """Discard all ephemeral workflow state."""
    user_sessions.pop(user_id, None)


# IMPORTANT: citizen content may exist only through the explicit ephemeral helpers above. It must never be persisted, serialized, logged, or sent to a durable Janavani repository.
# Do not persist this mapping, serialize it, log it, or send it to a storage adapter.
# A Telegram transport necessarily receives message content transiently; Janavani
# treats that processing as an ephemeral transport boundary, not citizen storage.


def set_ephemeral_issue(user_id: int, value: str) -> None:
    """Keep citizen content only in process memory for a short workflow window."""
    session = get_session(user_id)
    session["_ephemeral_issue"] = value
    session["_ephemeral_issue_expires"] = monotonic() + _EPHEMERAL_TTL_SECONDS


def get_ephemeral_issue(user_id: int) -> str | None:
    """Return transient issue content only while its short TTL is valid."""
    session = get_session(user_id)
    if monotonic() >= float(session.get("_ephemeral_issue_expires", 0.0)):
        clear_ephemeral_issue(user_id)
        return None
    return session.get("_ephemeral_issue")


def clear_ephemeral_issue(user_id: int) -> None:
    session = get_session(user_id)
    session["_ephemeral_issue"] = None
    session["_ephemeral_issue_expires"] = 0.0
