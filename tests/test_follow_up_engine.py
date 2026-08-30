from datetime import date

import pytest

from src.core.capabilities.follow_up_engine import SharedFollowUpEngine
from src.core.contracts.follow_up import FollowUpTrigger, TriggerKind


def trigger(interval=15, source="official-procedure-1"):
    return FollowUpTrigger(
        trigger_id="rti-response",
        kind=TriggerKind.RESPONSE_DEADLINE,
        label="verified response interval",
        source_id=source,
        interval_days=interval,
    )


def test_verified_interval_calculates_due_date():
    result = SharedFollowUpEngine().evaluate(trigger(), reference_date=date(2026, 9, 1))
    assert result.due_on == date(2026, 9, 16)
    assert result.requires_user_confirmation is True


def test_missing_interval_does_not_invent_deadline():
    result = SharedFollowUpEngine().evaluate(trigger(interval=None), reference_date=date(2026, 9, 1))
    assert result.due_on is None


def test_missing_verified_source_fails():
    with pytest.raises(ValueError):
        SharedFollowUpEngine().evaluate(trigger(source=""), reference_date=date(2026, 9, 1))


def test_due_check():
    result = SharedFollowUpEngine().evaluate(trigger(), reference_date=date(2026, 9, 1))
    assert SharedFollowUpEngine().is_due(result, on=date(2026, 9, 16))
