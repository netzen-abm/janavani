"""Retired legacy complaint tracker.

The historical implementation is preserved under archive/legacy/feedback/.
The canonical Case lifecycle and follow-up boundaries are now authoritative.

This compatibility tombstone intentionally fails closed so callers cannot
continue mutating or reading the legacy ratings JSONL as a case-tracking store.
"""


def get_complaint_status(*args, **kwargs) -> dict:
    """Fail closed; legacy complaint tracking is retired."""
    raise RuntimeError(
        "Legacy complaint tracking is retired; use the canonical Case lifecycle."
    )


def list_user_complaints(*args, **kwargs) -> list:
    """Fail closed; legacy complaint tracking is retired."""
    raise RuntimeError(
        "Legacy complaint tracking is retired; use the canonical Case lifecycle."
    )


def update_complaint_status(*args, **kwargs) -> str:
    """Fail closed; legacy complaint status mutation is retired."""
    raise RuntimeError(
        "Legacy complaint tracking is retired; use the canonical Case lifecycle."
    )
