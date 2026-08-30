"""Shared service facade for issue understanding providers."""

from dataclasses import dataclass
from typing import Optional

from .issue_understanding import IssueUnderstanding, IssueUnderstandingProvider


@dataclass(frozen=True)
class IssueUnderstandingResult:
    understanding: IssueUnderstanding
    language: str
    provider: str


class SharedIssueUnderstandingService:
    """Channel-neutral facade for deterministic or AI-assisted understanding."""

    def __init__(self, provider: IssueUnderstandingProvider, provider_name: str = "default"):
        self._provider = provider
        self._provider_name = provider_name

    def understand(self, issue_text: str, language: str = "en") -> IssueUnderstandingResult:
        if not issue_text or not issue_text.strip():
            raise ValueError("issue_text is required")
        result = self._provider.understand(issue_text.strip())
        return IssueUnderstandingResult(result, language, self._provider_name)
