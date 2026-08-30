"""Migration implementation of the shared Case capability.

This adapter isolates legacy JSONL persistence from all access surfaces.
It is intentionally temporary until the canonical Case repository is ready.
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
        except OSError:
            return CaseResult(ok=False, error_code="case_persistence_failed", message="The case could not be saved.")
        return CaseResult(ok=True, case=case)

    def get(self, case_id: str) -> CaseResult:
        from capabilities.tracking_file import LegacyComplaintTrackingCapability
        return LegacyComplaintTrackingCapability(self.file_path).get_status(case_id)

    def update(self, case_id: str, **changes):
        """Update a legacy JSONL case while keeping storage behind the capability."""
        records = []
        found = False
        try:
            with open(self.file_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if record.get("complaint_id") == case_id:
                        record.update({k: v for k, v in changes.items() if v is not None})
                        record["updated_at"] = datetime.now(timezone.utc).isoformat()
                        found = True
                    records.append(record)
        except (OSError, json.JSONDecodeError):
            return CaseResult(ok=False, error_code="case_persistence_failed", message="The case could not be updated.")

        if not found:
            return CaseResult(ok=False, error_code="case_not_found", message="Case not found.")

        try:
            with open(self.file_path, "w", encoding="utf-8") as handle:
                for record in records:
                    handle.write(json.dumps(record) + "\n")
        except OSError:
            return CaseResult(ok=False, error_code="case_persistence_failed", message="The case could not be updated.")

        return self.get(case_id)

    def update_status(self, case_id: str, status: CaseStatus):
        return self.update(case_id, status=status.value)

    def delete(self, case_id: str):
        return CaseResult(ok=False, error_code="not_implemented", message="Case deletion is not available in the migration adapter.")
