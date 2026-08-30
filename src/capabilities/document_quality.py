"""Deterministic document quality checks shared by every access surface."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QualityIssue:
    code: str
    field: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class QualityResult:
    ok: bool
    issues: tuple[QualityIssue, ...] = ()


class DocumentQualityCapability:
    """Validates structured document data without invoking AI."""

    def check(self, data: dict[str, Any]) -> QualityResult:
        issues: list[QualityIssue] = []
        authority = data.get("authority") or {}
        user = data.get("user") or {}

        if not authority.get("name"):
            issues.append(QualityIssue("missing_to", "authority.name", "A verified To authority is required."))
        if not authority.get("address"):
            issues.append(QualityIssue("missing_to_address", "authority.address", "A postal address is required before export."))
        if not data.get("subject"):
            issues.append(QualityIssue("missing_subject", "subject", "A subject is required."))
        if not data.get("issue"):
            issues.append(QualityIssue("missing_issue", "issue", "The civic issue description is required."))
        if not user.get("name"):
            issues.append(QualityIssue("missing_citizen_name", "user.name", "Citizen name is required when the selected action requires identification."))

        return QualityResult(ok=not issues, issues=tuple(issues))
