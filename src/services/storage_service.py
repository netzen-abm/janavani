"""Retired legacy complaint storage service.

The historical implementation is preserved under
``archive/legacy/storage/storage_service.py``.

The canonical Case lifecycle and repository boundaries are authoritative.
This compatibility tombstone fails closed so callers cannot continue writing
or reading the legacy ``database/complaints.jsonl`` store through this service.
"""


def save_complaint(*args, **kwargs):
    """Fail closed; legacy complaint persistence is retired."""
    raise RuntimeError(
        "Legacy complaint storage is retired; use the canonical Case lifecycle."
    )


def get_complaint_by_id(*args, **kwargs):
    """Fail closed; legacy complaint lookup is retired."""
    raise RuntimeError(
        "Legacy complaint storage is retired; use the canonical Case lifecycle."
    )
