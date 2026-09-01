"""Canonical complaint composition.

Composition is transport-independent. Rendering and delivery are separate
capabilities so the same complaint payload can be used by Web, Telegram,
WhatsApp, Android, iOS, or future surfaces.
"""

from __future__ import annotations

import datetime as _datetime
import uuid

try:
    from legal_brain import get_legal_advice
except Exception:  # Optional capability: document creation must remain usable.
    get_legal_advice = None


class ComplaintBuilder:
    """Build a structured complaint payload without rendering or delivery."""

    def build(
        self,
        user_name: str,
        user_address: str,
        office_id: str,
        issue_text: str,
        office: dict | None = None,
        subject: str | None = None,
        cc: list[dict] | None = None,
    ) -> dict:
        if not issue_text or not issue_text.strip():
            raise ValueError("issue_text is required")

        now = _datetime.datetime.now(_datetime.timezone.utc)
        payload = {
            "document_type": "complaint",
            "document_version": "1",
            "complaint_id": f"JV-{now:%Y%m%d}-{uuid.uuid4().hex[:10].upper()}",
            "date": now.date().isoformat(),
            "title": "FORMAL COMPLAINT",
            "user": {
                "name": user_name,
                "address": user_address,
            },
            "office_id": str(office_id),
            "issue": issue_text.strip(),
        }

        if office:
            payload["to"] = dict(office)
        if subject:
            payload["subject"] = subject.strip()
        if cc:
            payload["cc"] = [dict(item) for item in cc]

        if get_legal_advice is not None:
            try:
                legal = get_legal_advice(issue_text)
                if legal is not None:
                    payload["legal_analysis"] = legal
            except Exception:
                pass

        return payload


def build_complaint(user_name: str, user_address: str, office_id: str, issue_text: str) -> dict:
    """Backward-compatible function facade over the canonical builder."""
    return ComplaintBuilder().build(user_name, user_address, office_id, issue_text)
