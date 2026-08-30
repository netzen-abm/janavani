"""Temporary adapter from the legacy complaint store to Case Tracking.

This adapter isolates legacy JSONL storage from access surfaces. It is a
migration bridge; the canonical Case repository will replace it later.
"""

import json

from capabilities.case import Case, CaseStatus
from capabilities.tracking import CaseTrackingCapability, TrackingResult


class LegacyComplaintTrackingCapability(CaseTrackingCapability):
    def __init__(self, file_path: str = "database/complaints.jsonl"):
        self.file_path = file_path

    def get_status(self, case_id: str) -> TrackingResult:
        try:
            with open(self.file_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    record = json.loads(line)
                    if record.get("complaint_id") != case_id:
                        continue

                    status = str(record.get("status", "Pending")).lower()
                    try:
                        case_status = CaseStatus(status)
                    except ValueError:
                        case_status = CaseStatus.TRACKING

                    case = Case(
                        case_id=case_id,
                        case_type="complaint",
                        status=case_status,
                        created_at=str(record.get("created_at", "")),
                        updated_at=str(record.get("created_at", "")),
                        issue=record.get("issue"),
                        jurisdiction={"district": record.get("district")},
                        authority=record.get("office"),
                        metadata={"legacy_record": True, "category": record.get("category"), "department": record.get("department")},
                    )
                    return TrackingResult(ok=True, case=case)
        except (FileNotFoundError, json.JSONDecodeError):
            return TrackingResult(ok=False, error_code="tracking_unavailable", message="Case tracking is temporarily unavailable.")

        return TrackingResult(ok=False, error_code="case_not_found", message="Case not found.")
