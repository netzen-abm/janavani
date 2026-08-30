from datetime import date

import pytest

from src.core.capabilities.procedure_trigger_registry import SharedProcedureTriggerRegistry
from src.core.contracts.procedure_trigger import ProcedureTrigger, VerificationStatus


def record(status=VerificationStatus.UNVERIFIED):
    return ProcedureTrigger(
        trigger_id="rti-followup-1",
        action="follow_up",
        jurisdiction="IN-KL",
        condition="verified procedural condition",
        trigger="verified trigger",
        source_id="official-source-1",
        source_title="Official procedure source",
        source_url="https://example.gov.in/procedure",
        effective_from=date(2026, 1, 1),
        verification=status,
    )


def test_unverified_record_never_drives_verified_lookup():
    registry = SharedProcedureTriggerRegistry((record(),))
    assert registry.get_verified(action="follow_up", jurisdiction="IN-KL") == ()


def test_verified_current_record_is_returned():
    registry = SharedProcedureTriggerRegistry((record(),))
    registry.verify("rti-followup-1")
    assert len(registry.get_verified(action="follow_up", jurisdiction="IN-KL", on=date(2026, 8, 30))) == 1


def test_stale_record_is_excluded():
    registry = SharedProcedureTriggerRegistry((record(),))
    registry.verify("rti-followup-1")
    registry.mark_stale("rti-followup-1")
    assert registry.get_verified(action="follow_up", jurisdiction="IN-KL") == ()


def test_provenance_is_required():
    with pytest.raises(ValueError):
        registry = SharedProcedureTriggerRegistry()
        registry.register(ProcedureTrigger(
            "bad", "follow_up", "IN-KL", "condition", "trigger", "", "", ""
        ))
