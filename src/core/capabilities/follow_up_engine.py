"""Shared follow-up engine.

It consumes verified procedure metadata. It never invents statutory deadlines.
The engine creates a follow-up recommendation/event; it does not send a
message, submit a complaint, or contact an authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from src.core.contracts.follow_up import FollowUpTrigger, TriggerKind


@dataclass(frozen=True)
class FollowUpRecommendation:
    trigger_id: str
    due_on: date | None
    reason: str
    requires_user_confirmation: bool = True


class SharedFollowUpEngine:
    def evaluate(self, trigger: FollowUpTrigger, *, reference_date: date) -> FollowUpRecommendation:
        if trigger.requires_verification and not trigger.source_id.strip():
            raise ValueError("verified procedure source is required")
        if trigger.interval_days is None:
            return FollowUpRecommendation(
                trigger.trigger_id,
                None,
                "Follow-up trigger exists but no verified interval was supplied; user/event confirmation is required.",
            )
        if trigger.interval_days < 0:
            raise ValueError("interval_days cannot be negative")
        due_on = reference_date + timedelta(days=trigger.interval_days)
        return FollowUpRecommendation(
            trigger.trigger_id,
            due_on,
            f"Follow-up evaluated from verified procedure trigger {trigger.trigger_id}.",
        )

    def is_due(self, recommendation: FollowUpRecommendation, *, on: date) -> bool:
        return recommendation.due_on is not None and on >= recommendation.due_on
