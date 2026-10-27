"""Escalation checks for legacy JSONL-backed complaint records."""
from datetime import datetime, timedelta

from src.services.escalation_rules import get_escalation_targets
from src.storage.jsonl_store import read_jsonl_records, update_jsonl_records

DATA_FILE = "database/ratings.jsonl"
ESCALATION_DAYS = 3


def check_overdue_complaints():
    """Return submitted complaints older than the escalation threshold."""
    try:
        entries = read_jsonl_records(DATA_FILE)
    except FileNotFoundError:
        return []

    overdue = []
    now = datetime.now()
    for entry in entries:
        if entry["status"] != "submitted":
            continue
        created_time = datetime.fromisoformat(entry["timestamp"])
        if now - created_time > timedelta(days=ESCALATION_DAYS):
            entry["escalation_targets"] = get_escalation_targets(
                entry.get("category", "General")
            )
            overdue.append(entry)
    return overdue


def mark_escalated(complaint_id: str) -> str:
    """Mark the matching complaint acknowledged after an escalation action."""
    try:
        updated = update_jsonl_records(
            DATA_FILE, "complaint_id", complaint_id, {"status": "acknowledged"}
        )
    except FileNotFoundError:
        return "Database not found"
    return "Escalated" if updated else "Not found"
