"""Migration implementation of the shared Case capability.

This creates a canonical Case first and keeps the legacy document builder out
of the channel adapter. Persistence remains a migration concern until the
canonical Case repository is introduced.
"""

from datetime import datetime, timezone
import json
import uuid

from capabilities.case import Case, CaseCapability, CaseResult, CaseStatus


class FileCaseCapability(CaseCapability):
    def __init__(self, file_path: str = "database/complaints.jsonl"):
        self.file_path = file_path

    def create(self, *, case_type: str, issue: str | None = None, metadata=None) -> CaseResult:
        case_id = f"JNV-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        case = Case(
            case_id=case_id,
            case_type=case_type,
            status=CaseStatus.IN_PROGRESS,
            created_at=now,
            updated_at=now,
            issue=issue,
            metadata=dict(metadata or {}),
        )
        record = {
            "complaint_id": case_id,
            "issue": issue,
            "category": case.metadata.get("category"),
            "department": case.metadata.get("department"),
            "district": case.metadata.get("district"),
            "office": case.metadata.get("office"),
            "created_at": now,
            "status": case.status.value,
        }
        try:
            with open(self.file_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except OSError as exc:
            return CaseResult(ok=False, error_code="case_persistence_failed", message="The case could not be saved.")
        return CaseResult(ok=True, case=case)

    def get(self, case_id: str) -> CaseResult:
        from capabilities.tracking_file import LegacyComplaintTrackingCapability
        return LegacyComplaintTrackingCapability(self.file_path).get_status(case_id)

    def update(self, case_id: str, **changes):
        return CaseResult(ok=False, error_code="not_implemented", message="Case update is not available in the migration adapter.")

    def update_status(self, case_id: str, status: CaseStatus):
        return CaseResult(ok=False, error_code="not_implemented", message="Case status update is not available in the migration adapter.")

    def delete(self, case_id: str):
        return CaseResult(ok=False, error_code="not_implemented", message="Case deletion is not available in the migration adapter.")
