"""In-memory state for an active Telegram conversation.

This store is process-local and is not durable across restarts or instances.
Persistent case tracking belongs in the storage layer, not this session store.
"""

user_sessions = {}


def get_session(user_id):
    """Return the existing session or initialize the canonical default shape."""
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
    """Clear transient conversation state for the given user."""
    user_sessions.pop(user_id, None)
