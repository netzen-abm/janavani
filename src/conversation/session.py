"""Non-sensitive Telegram workflow state and TTL-scoped transient issue content.

Workflow metadata and raw citizen narratives have separate in-process stores.
The narrative buffer has a short TTL and is purged by the Telegram runtimes.
Neither store is durable.
"""
from __future__ import annotations

from time import monotonic

from conversation.state import user_states

user_sessions: dict[int, dict] = {}
_ephemeral_issues: dict[int, tuple[str, float]] = {}
_ephemeral_anonymous_drafts: dict[int, tuple[list, float]] = {}
_EPHEMERAL_TTL_SECONDS = 15 * 60


def get_session(user_id: int) -> dict:
    """Return non-sensitive workflow metadata without citizen-authored narrative."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "workflow": "Complaint",
            "district": "",
            "department": "",
            "offices": [],
            "identity_mode": "anonymous",
            "case_id": "",
            "format": "",
            "document_id": "",
            "office": {
                "office_id": "",
                "office_name": "",
                "office_address": "",
                "department": "",
                "district": "",
            },
        }
    return user_sessions[user_id]


def clear_session(user_id: int) -> None:
    """Discard workflow metadata and any associated transient citizen content."""
    user_sessions.pop(user_id, None)
    _ephemeral_issues.pop(user_id, None)
    _ephemeral_anonymous_drafts.pop(user_id, None)


def set_ephemeral_issue(user_id: int, value: str) -> None:
    """Keep citizen narrative in a separate in-memory buffer for at most 15 minutes."""
    get_session(user_id)
    _ephemeral_issues[user_id] = (value, monotonic() + _EPHEMERAL_TTL_SECONDS)


def get_ephemeral_issue(user_id: int) -> str | None:
    """Return transient issue content only while its short TTL is valid."""
    entry = _ephemeral_issues.get(user_id)
    if entry is None:
        return None
    value, expires_at = entry
    if monotonic() >= expires_at:
        _ephemeral_issues.pop(user_id, None)
        return None
    return value


def purge_expired_ephemeral_issues(now: float | None = None) -> int:
    """Remove expired issue text even when its owner abandons the workflow."""
    current = monotonic() if now is None else now
    expired = [
        user_id for user_id, (_, expires_at) in _ephemeral_issues.items()
        if current >= expires_at
    ]
    for user_id in expired:
        _ephemeral_issues.pop(user_id, None)
        # Once the only copy of the citizen narrative expires, its remaining
        # process-local workflow metadata can no longer complete the same flow.
        user_sessions.pop(user_id, None)
        user_states.pop(user_id, None)
    return len(expired)


def clear_ephemeral_issue(user_id: int) -> None:
    """Clear only the citizen-content buffer; preserve non-sensitive workflow metadata."""
    _ephemeral_issues.pop(user_id, None)
