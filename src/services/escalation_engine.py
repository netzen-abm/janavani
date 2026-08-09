# src/services/escalation_engine.py

import json
from datetime import datetime, timedelta
from src.services.escalation_rules import get_escalation_targets

DATA_FILE = "database/ratings.jsonl"
ESCALATION_DAYS = 3


def check_overdue_complaints():
    """
    Returns complaints that need escalation
    """

    overdue = []

    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                entry = json.loads(line)

                # Only check submitted complaints
                if entry["status"] != "submitted":
                    continue

                created_time = datetime.fromisoformat(entry["timestamp"])

                if datetime.now() - created_time > timedelta(days=ESCALATION_DAYS):
                    # Attach escalation targets
                    category = entry.get("category", "General")
                    entry["escalation_targets"] = get_escalation_targets(category)

                    overdue.append(entry)

        return overdue

    except FileNotFoundError:
        return []


def mark_escalated(complaint_id: str) -> str:
    """
    Marks complaint as escalated
    """

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
                    entry["status"] = "acknowledged"
                    updated = True

                entries.append(entry)

        with open(DATA_FILE, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        if updated:
            return "Escalated"
        return "Not found"

    except FileNotFoundError:
        return "Database not found"