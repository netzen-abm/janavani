"""Canonical complaint composition.

This module creates structured document data only. Rendering and delivery are
separate capabilities. Legal/AI enrichment is optional and failure-tolerant.
"""

from __future__ import annotations

import datetime as _datetime
import uuid

try:
    from legal_brain import get_legal_advice
except Exception:  # Optional capability: basic document creation must survive it.
    get_legal_advice = None


class ComplaintBuilder:
    """Build a purpose-bound complaint payload without rendering or delivery."""

    def build(self, user_name: str, user_address: str, office_id: str, issue_text: str) -> dict:
        if not issue_text or not issue_text.strip():
            raise ValueError("issue_text is required")

        now = _datetime.datetime.now(_datetime.timezone.utc)
        legal = None
        if get_legal_advice is not None:
            try:
                legal = get_legal_advice(issue_text)
            except Exception:
                legal = None

        payload = {
            "document_type": "complaint",
            "document_version": "1",
            "complaint_id": f"JV-{now:%Y%m%d}-{uuid.uuid4().hex[:10].upper()}",
            "date": now.date().isoformat(),
            "title": "FORMAL COMPLAINT",
            "user": {"name": user_name, "address": user_address},
            "office_id": str(office_id),
            "issue": issue_text.strip(),
        }
        if legal is not None:
            payload["legal_analysis"] = legal
        return payload


def build_complaint(user_name: str, user_address: str, office_id: str, issue_text: str) -> dict:
    """Backward-compatible function facade over the canonical builder."""
    return ComplaintBuilder().build(user_name, user_address, office_id, issue_text)
