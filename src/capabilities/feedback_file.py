"""Legacy ratings provider adapted to the shared Feedback capability."""

import datetime
import hashlib
import json

from capabilities.feedback import FeedbackCapability, FeedbackResult


class JsonlFeedbackCapability(FeedbackCapability):
    def __init__(self, file_path: str = "database/ratings.jsonl"):
        self.file_path = file_path

    def submit_rating(
        self,
        *,
        authority_id: str,
        rating: int,
        comment: str | None = None,
        user_reference: str | None = None,
    ) -> FeedbackResult:
        if not 1 <= rating <= 5:
            return FeedbackResult(False, message="Rating must be between 1 and 5.", error_code="invalid_rating")

        feedback_id = f"FB{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        user_hash = None
        if user_reference:
            user_hash = hashlib.sha256(user_reference.encode()).hexdigest()[:10]

        entry = {
            "feedback_id": feedback_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "authority_id": authority_id,
            "rating": rating,
            "comment": comment,
            "user_hash": user_hash,
        }

        try:
            with open(self.file_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry) + "\n")
        except OSError:
            return FeedbackResult(False, message="Feedback is temporarily unavailable.", error_code="feedback_unavailable")

        return FeedbackResult(True, feedback_id=feedback_id, message="Thank you. Your feedback was recorded.")
