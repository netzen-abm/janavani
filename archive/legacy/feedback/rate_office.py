"""Historical rating service preserved under the archive-first policy.

Canonical replacement: src/capabilities/accountability_feedback.py.
The active Telegram adapter must use the canonical capability.
"""

import datetime
import hashlib
import json
import os


def save_rating(office_id: str, rating: int, issue: str, user_phone: str = "anonymous") -> str:
    try:
        rating_val = int(rating)
    except Exception:
        return "Invalid rating: must be an integer between 1 and 5."
    if rating_val < 1 or rating_val > 5:
        return "Invalid rating: must be between 1 and 5."
    try:
        user_hash = hashlib.sha256(str(user_phone).encode()).hexdigest()[:10]
    except Exception:
        user_hash = "anon"
    complaint_id = f"JV{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    entry = {
        "complaint_id": complaint_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "office_id": str(office_id),
        "rating": rating_val,
        "issue": issue,
        "user_hash": user_hash,
        "status": "submitted",
    }
    try:
        os.makedirs("database", exist_ok=True)
        with open("database/ratings.jsonl", "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except Exception:
                pass
    except Exception as exc:
        return f"Failed to save rating: {exc}"
    return f"Saved. Your Complaint ID: {complaint_id}. Use this to track."
