"""Channel-neutral Feedback capability."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FeedbackResult:
    ok: bool
    feedback_id: str | None = None
    message: str | None = None
    error_code: str | None = None


class FeedbackCapability(Protocol):
    def submit_rating(
        self,
        *,
        authority_id: str,
        rating: int,
        comment: str | None = None,
        user_reference: str | None = None,
    ) -> FeedbackResult: ...
