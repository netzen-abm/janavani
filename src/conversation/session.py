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

from copy import deepcopy
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
            "_ephemeral_civic_draft": None,
            "_ephemeral_civic_draft_expires": 0.0,
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

def purge_expired_ephemeral_issues() -> int:
    """Erase expired citizen narratives even when the user sends no later update."""
    now = monotonic()
    purged = 0
    for session in user_sessions.values():
        if session.get("_ephemeral_issue") is not None and now >= float(
            session.get("_ephemeral_issue_expires", 0.0)
        ):
            session["_ephemeral_issue"] = None
            session["_ephemeral_issue_expires"] = 0.0
            purged += 1
        if session.get("_ephemeral_civic_draft") is not None and now >= float(
            session.get("_ephemeral_civic_draft_expires", 0.0)
        ):
            session["_ephemeral_civic_draft"] = None
            session["_ephemeral_civic_draft_expires"] = 0.0
            purged += 1
    return purged

async def run_ephemeral_issue_cleanup() -> None:
    """Periodically erase expired issue text while the Telegram webhook is live."""
    import asyncio

    while True:
        await asyncio.sleep(30)
        purge_expired_ephemeral_issues()

_CIVIC_DRAFT_FIELDS = {
    "template_id", "issue", "subject", "existing_draft", "jurisdiction",
    "requested_documents",
}
_CIVIC_DRAFT_TEXT_LIMITS = {
    "template_id": 80, "issue": 5_000, "subject": 200,
    "existing_draft": 8_000, "jurisdiction": 300,
}


def set_ephemeral_civic_draft(user_id: int, value: dict) -> None:
    """Store an allow-listed draft workflow in process memory for one short TTL."""
    if not isinstance(value, dict) or set(value) - _CIVIC_DRAFT_FIELDS:
        raise ValueError("Unsupported transient civic-draft fields")
    if not {"template_id", "issue"} <= set(value):
        raise ValueError("Transient civic draft requires a template and issue field")
    for key, limit in _CIVIC_DRAFT_TEXT_LIMITS.items():
        text = value.get(key, "")
        if not isinstance(text, str):
            raise ValueError("Transient civic-draft text fields must be strings")
        if len(text) > limit:
            raise ValueError(f"Transient civic-draft field {key} exceeds its limit")
    if not value["template_id"].strip():
        raise ValueError("Transient civic draft requires a template ID")
    records = value.get("requested_documents", [])
    if not isinstance(records, (list, tuple)) or any(not isinstance(item, str) for item in records):
        raise ValueError("Transient requested records must be a list of strings")
    if len(records) > 12 or any(not item.strip() or len(item) > 800 for item in records):
        raise ValueError("Transient requested records exceed limits")
    session = get_session(user_id)
    session["_ephemeral_civic_draft"] = deepcopy({**value, "requested_documents": list(records)})
    session["_ephemeral_civic_draft_expires"] = monotonic() + _EPHEMERAL_TTL_SECONDS


def get_ephemeral_civic_draft(user_id: int) -> dict | None:
    """Return a copy of the transient draft while its TTL remains valid."""
    session = get_session(user_id)
    if monotonic() >= float(session.get("_ephemeral_civic_draft_expires", 0.0)):
        clear_ephemeral_civic_draft(user_id)
        return None
    value = session.get("_ephemeral_civic_draft")
    return deepcopy(value) if isinstance(value, dict) else None


def clear_ephemeral_civic_draft(user_id: int) -> None:
    """Erase only the transient AI-drafting flow, not an unrelated Case session."""
    session = get_session(user_id)
    session["_ephemeral_civic_draft"] = None
    session["_ephemeral_civic_draft_expires"] = 0.0
