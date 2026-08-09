# src/services/escalation_runner.py

from src.services.escalation_engine import check_overdue_complaints, mark_escalated


def run_escalation_cycle():
    """
    Runs escalation logic across all complaints
    """

    overdue = check_overdue_complaints()

    if not overdue:
        return "No complaints to escalate"

    results = []

    for complaint in overdue:
        complaint_id = complaint["complaint_id"]

        status = mark_escalated(complaint_id)

        results.append({
            "complaint_id": complaint_id,
            "action": status,
            "targets": complaint.get("escalation_targets", [])
        })

    return results