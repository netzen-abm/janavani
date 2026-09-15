"""Retired legacy escalation engine.

The historical implementation is preserved under archive/legacy/escalation/.
The canonical escalation boundary is src/capabilities/escalation.py.
"""


def check_overdue_complaints():
    """Fail closed; the historical escalation engine is retired."""
    raise RuntimeError(
        "Legacy escalation engine is retired; use the canonical EscalationCapability."
    )


def mark_escalated(complaint_id: str) -> str:
    """Fail closed; legacy escalation mutation is retired."""
    raise RuntimeError(
        "Legacy escalation mutation is retired; use the canonical civic-action flow."
    )
