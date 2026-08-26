"""Compatibility service for complaint persistence.

Business-facing callers keep the historical function names while persistence
is delegated to the provider-neutral repository boundary. The repository can
later be swapped for the canonical durable adapter without changing callers.
"""

from __future__ import annotations

from typing import Any

from storage.complaint_repository import ComplaintRepository


_repository = ComplaintRepository()


def save_complaint(session: dict[str, Any]) -> None:
    """Persist the complaint session through the repository boundary."""
    record = {
        "complaint_id": session.get("complaint_id"),
        "issue": session.get("issue"),
        "category": session.get("category"),
        "department": session.get("department"),
        "district": session.get("district"),
        "office": session.get("office"),
        "status": "Pending",
    }
    _repository.save(record)


def get_complaint_by_id(complaint_id: str) -> dict[str, Any] | None:
    """Fetch a complaint through the repository boundary."""
    return _repository.get_by_id(complaint_id)


__all__ = ["get_complaint_by_id", "save_complaint"]
