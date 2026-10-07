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

user_sessions: dict[int, dict] = {}


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
        }
    return user_sessions[user_id]


def clear_session(user_id: int) -> None:
    """Discard all ephemeral workflow state."""
    user_sessions.pop(user_id, None)


# IMPORTANT: values added by future workflow steps must remain ephemeral.
# Do not persist this mapping, serialize it, log it, or send it to a storage adapter.
# A Telegram transport necessarily receives message content transiently; Janavani
# treats that processing as an ephemeral transport boundary, not citizen storage.
