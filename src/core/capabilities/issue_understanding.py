"""Channel-neutral issue understanding capability."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class IssueUnderstanding:
    """Normalized understanding of a citizen-described issue."""

    category: str
    department: str
    confidence: float = 0.0
    source: str = "rule_based"


class IssueUnderstandingProvider(Protocol):
    """Provider interface; implementations may be deterministic or AI-backed."""

    def understand(self, issue_text: str) -> IssueUnderstanding:
        ...
