# src/services/track_complaint.py

import json

DATA_FILE = "database/ratings.jsonl"

VALID_STATUSES = {
    "submitted",
    "acknowledged",
    "in_progress",
    "resolved",
    "rejected"
}


def get_complaint_status(complaint_id: str, user_hash: str) -> dict:
    """
    Securely fetch complaint status
    """

    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                entry = json.loads(line)

                if (
                    entry["complaint_id"] == complaint_id
                    and entry["user_hash"] == user_hash
                ):
                    return {
                        "status": entry["status"],
                        "issue": entry["issue"],
                        "office_id": entry["office_id"],
                        "timestamp": entry["timestamp"]
                    }

        return {"error": "Complaint not found or access denied"}

    except FileNotFoundError:
        return {"error": "No complaint database found"}


def list_user_complaints(user_hash: str) -> list:
    """
    List all complaints for a user
    """

    results = []

    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                entry = json.loads(line)

                if entry["user_hash"] == user_hash:
                    results.append({
                        "complaint_id": entry["complaint_id"],
                        "status": entry["status"],
                        "issue": entry["issue"]
                    })

        return results

    except FileNotFoundError:
        return []


def update_complaint_status(complaint_id: str, new_status: str) -> str:
    """
    Update complaint status (admin/system use)
    """

    # ✅ VALIDATION (CRITICAL)
    if new_status not in VALID_STATUSES:
        return "Invalid status"

    updated = False
    entries = []

    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                entry = json.loads(line)

                if entry["complaint_id"] == complaint_id:
                    entry["status"] = new_status
                    updated = True

                entries.append(entry)

        # rewrite file
        with open(DATA_FILE, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        if updated:
            return f"Status updated to {new_status}"
        else:
            return "Complaint not found"

    except FileNotFoundError:
        return "Database not found"