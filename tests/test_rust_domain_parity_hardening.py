"""Regression specification for the canonical Rust CivicCase event boundary.

These tests intentionally document invariants that must hold before the Rust
aggregate is considered parity-hardened. They are kept separate from the
existing Python domain tests because the implementation under test is Rust.
"""

from pathlib import Path


RUST_SOURCE = Path("crates/janavani-core/src/lib.rs")


def test_rust_acknowledgement_does_not_mutate_only_the_returned_event():
    source = RUST_SOURCE.read_text(encoding="utf-8")
    assert ".map(|mut event|" not in source
    assert "event.notes = notes;" not in source


def test_rust_status_event_has_distinct_notes_and_source_ref_parameters():
    source = RUST_SOURCE.read_text(encoding="utf-8")
    assert "source_ref: Option<String>,\n        notes: Option<String>," in source


def test_rust_notes_are_not_passed_as_source_refs():
    source = RUST_SOURCE.read_text(encoding="utf-8")
    for event_type in ("FollowUp", "Response", "Resolved", "Escalated", "Correction"):
        marker = f"CaseEventType::{event_type}"
        assert marker in source
    # Domain operations must explicitly assign notes rather than using the
    # source_ref argument as a positional notes carrier.
    assert "CaseEventType::FollowUp, actor_id, None, notes)" not in source
    assert "CaseEventType::Response, actor_id, None, notes)" not in source
    assert "CaseEventType::Resolved, actor_id, None, notes)" not in source
    assert "CaseEventType::Escalated, actor_id, None, notes)" not in source
    assert "CaseEventType::Correction, actor_id, None, notes)" not in source


def test_rust_mutations_validate_before_state_commit():
    source = RUST_SOURCE.read_text(encoding="utf-8")
    # The hardening implementation must not retain the known pattern of
    # changing status immediately before an event-recording operation that can
    # reject duplicate event IDs.
    assert "self.status = CaseStatus::Acknowledged;\n        self.status_event(" not in source
    assert "self.status = CaseStatus::Submitted;\n        self.status_event(" not in source
    assert "self.status = CaseStatus::Closed;\n        self.status_event(" not in source
