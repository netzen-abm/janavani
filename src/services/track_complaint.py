"""Authorized status lookup and updates for legacy JSONL complaint records."""
from src.storage.jsonl_store import read_jsonl_records, write_jsonl_records

DATA_FILE = "database/ratings.jsonl"

VALID_STATUSES = {
    "submitted",
    "acknowledged",
    "in_progress",
    "resolved",
    "rejected",
}


def get_complaint_status(complaint_id: str, user_hash: str) -> dict:
    """Fetch status only when complaint ID and owner hash both match."""
    try:
        entries = read_jsonl_records(DATA_FILE)
    except FileNotFoundError:
        return {"error": "No complaint database found"}

    for entry in entries:
        if (
            entry["complaint_id"] == complaint_id
            and entry["user_hash"] == user_hash
        ):
            return {
                "status": entry["status"],
                "issue": entry["issue"],
                "office_id": entry["office_id"],
                "timestamp": entry["timestamp"],
            }
    return {"error": "Complaint not found or access denied"}


def list_user_complaints(user_hash: str) -> list:
    """List complaint summaries belonging to the requested owner hash."""
    try:
        entries = read_jsonl_records(DATA_FILE)
    except FileNotFoundError:
        return []

    return [
        {
            "complaint_id": entry["complaint_id"],
            "status": entry["status"],
            "issue": entry["issue"],
        }
        for entry in entries
        if entry["user_hash"] == user_hash
    ]


def update_complaint_status(complaint_id: str, new_status: str) -> str:
    """Update status; intended for authorized administrative/system callers."""
    if new_status not in VALID_STATUSES:
        return "Invalid status"

    try:
        entries = read_jsonl_records(DATA_FILE)
    except FileNotFoundError:
        return "Database not found"

    updated = False
    for entry in entries:
        if entry["complaint_id"] == complaint_id:
            entry["status"] = new_status
            updated = True

    write_jsonl_records(DATA_FILE, entries)
    if updated:
        return f"Status updated to {new_status}"
    return "Complaint not found"
