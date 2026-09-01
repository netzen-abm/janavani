# src/services/rate_office.py
# Saves rating and complaint to file (hardened)

import json
import datetime
import hashlib
import os
from typing import Optional


def save_rating(office_id: str, rating: int, issue: str, user_phone: str = "anonymous") -> str:
    """
    Saves rating to database/ratings.jsonl
    rating: 1 to 5
    Returns: Complaint ID or error message
    """

    # Validate rating
    try:
        rating_val = int(rating)
    except Exception:
        return "Invalid rating: must be an integer between 1 and 5."

    if rating_val < 1 or rating_val > 5:
        return "Invalid rating: must be between 1 and 5."

    # Hash the phone for privacy. We never store real number
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
        "status": "submitted"
    }

    # Ensure directory exists
    try:
        os.makedirs("database", exist_ok=True)
    except Exception as e:
        return f"Failed to prepare storage directory: {e}"

    # Save to file. Each line = 1 complaint
    path = "database/ratings.jsonl"
    try:
        # append and fsync to reduce risk of lost data on crash
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                # fsync may not be supported on some filesystems; ignore safely
                pass
    except Exception as e:
        return f"Failed to save rating: {e}"

    return f"Saved. Your Complaint ID: {complaint_id}. Use this to track."
