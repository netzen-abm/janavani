"""Conversation session storage.

The current runtime keeps session state in memory.  The storage boundary is
kept behind these functions so the implementation can later move to a shared
persistent adapter without changing conversation steps.
"""

user_sessions = {}


def get_session(user_id):
    """Return the mutable session for a user, creating it on first access."""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "workflow": "Complaint",
            "issue": "",
            "document": "",
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
            "name": "",
            "address": "",
            "phone": "",
            "email": "",
            "photo": None,
        }
    return user_sessions[user_id]


def clear_session(user_id):
    """Discard a user's in-memory session."""
    user_sessions.pop(user_id, None)
