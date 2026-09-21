"""Compatibility import for the canonical issue-classification capability."""

from src.capabilities.issue_classification import IssueClassification, classify_issue

__all__ = ["IssueClassification", "classify_issue"]
