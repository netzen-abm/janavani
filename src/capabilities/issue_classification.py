"""Canonical deterministic civic-issue classification capability."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IssueClassification:
    category: str
    department: str


_RULES: tuple[tuple[tuple[str, ...], IssueClassification], ...] = (
    (
        ("garbage", "waste", "trash", "clean", "drain", "sewage"),
        IssueClassification("Sanitation", "Municipality / Panchayat"),
    ),
    (
        ("road", "pothole", "street", "bridge"),
        IssueClassification("Infrastructure", "PWD (Public Works Department)"),
    ),
    (
        ("water", "pipe", "drinking water", "leak"),
        IssueClassification("Water Supply", "Water Authority"),
    ),
    (
        ("electricity", "power", "current", "transformer"),
        IssueClassification("Electricity", "Electricity Board"),
    ),
)


def classify_issue(issue: str) -> IssueClassification:
    """Classify civic issue text without owning Case or transport state."""
    if not isinstance(issue, str):
        raise TypeError("issue must be text")
    normalized = issue.strip().lower()
    if not normalized:
        raise ValueError("issue must not be empty")
    for keywords, result in _RULES:
        if any(keyword in normalized for keyword in keywords):
            return result
    return IssueClassification("General", "Local Authority")
