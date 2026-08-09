# src/services/track_complaint.py

import json


DATA_FILE = "database/ratings.jsonl"


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