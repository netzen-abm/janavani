# conversation/session.py

"""
Stores user conversation data.

Currently stored in memory.

Later this will be stored in Supabase.
"""

user_sessions = {}


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

    # Office
    "office": "",
    "office_id": "",

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
