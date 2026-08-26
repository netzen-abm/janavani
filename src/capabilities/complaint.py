"""Channel-neutral complaint capability.

This module owns reusable complaint intake/classification/composition. It does
not import Telegram, WhatsApp, Messenger, or other interface SDKs.
"""

from __future__ import annotations

from typing import Any

from src.platform.contracts import CapabilityRequest, CapabilityResult
from src.documents.complaint_builder import build_complaint
from src.services.issue_classifier import classify_issue


class ComplaintCapability:
    """Handle normalized complaint requests independently of the interface."""

    capability = "complaint"

    def handle(self, request: CapabilityRequest) -> CapabilityResult:
        text = str(request.payload.get("text") or "").strip()
        if not text:
            return CapabilityResult(
                status="rejected",
                capability=self.capability,
                message="Complaint text is required.",
            )

        classification = classify_issue(text)
        complaint = build_complaint(
            user_name="Anonymous",
            user_address="Not Provided",
            office_id=str(request.payload.get("office_id") or "1"),
            issue_text=text,
        )

        return CapabilityResult(
            status="completed",
            capability=self.capability,
            message="Complaint prepared.",
            data={
                "issue": text,
                "category": classification.get("category"),
                "department": classification.get("department"),
                "complaint": complaint,
            },
        )
