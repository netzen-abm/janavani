# conversation/session.py

"""
Stores user conversation data.

Currently stored in memory.

Later this will be stored in Supabase.
"""

user_sessions = {}

sessions = {}

def get_session(user_id):
    if user_id not in sessions:
        sessions[user_id] = {}
    return sessions[user_id]


def get_session(user_id):

    if user_id not in user_sessions:

        user_sessions[user_id] = {

    # Workflow
    "workflow": "Complaint",

    # Citizen Issue
    "issue": "",

    # Selected Document
    "document": "",

    # Location
    "district": "",
    "department": "",

    # Office Search Results
    "offices": [],

    # Selected Office
    "office": {
        "office_id": "",
        "office_name": "",
        "office_address": "",
        "department": "",
        "district": "",
    },

    # Identity
    "identity_mode": "anonymous",

    # Citizen Details
    "name": "",
    "address": "",
    "phone": "",
    "email": "",

    # Attachment
    "photo": None,
}

    return user_sessions[user_id]


def clear_session(user_id):

    if user_id in user_sessions:
        del user_sessions[user_id]
