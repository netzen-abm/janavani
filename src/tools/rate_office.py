# src/tools/rate_office.py
# Saves rating and complaint to file

import json
import datetime
import hashlib

def save_rating(office_id: str, rating: int, issue: str, user_phone: str = "anonymous") -> str:
    """
    Saves rating to ratings.jsonl
    rating: 1 to 5
    Returns: Complaint ID
    """
    # Hash the phone for privacy. We never store real number
    user_hash = hashlib.sha256(user_phone.encode()).hexdigest()[:10]

    complaint_id = f"JV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    entry = {
        "complaint_id": complaint_id,
        "timestamp": str(datetime.datetime.now()),
        "office_id": office_id,
        "rating": rating,
        "issue": issue,
        "user_hash": user_hash,
        "status": "submitted"
    }

    # Save to file. Each line = 1 complaint
    with open("database/ratings.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

    return f"Saved. Your Complaint ID: {complaint_id}. Use this to track."
