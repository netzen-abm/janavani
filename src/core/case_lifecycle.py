"""Canonical status-transition contract for the CivicCase lifecycle.

This module is deliberately channel-neutral. Access surfaces must consume the
same lifecycle rules rather than implementing their own transition graph.
"""
from __future__ import annotations

from typing import Mapping

from src.core.civic_case import CaseStatus


CASE_STATUS_TRANSITIONS: Mapping[CaseStatus, frozenset[CaseStatus]] = {
    CaseStatus.DRAFT: frozenset({CaseStatus.REVIEW}),
    CaseStatus.REVIEW: frozenset({CaseStatus.REVIEW, CaseStatus.READY}),
    CaseStatus.READY: frozenset({CaseStatus.READY, CaseStatus.SUBMITTING}),
    CaseStatus.SUBMITTING: frozenset({CaseStatus.SUBMITTING, CaseStatus.QUEUED, CaseStatus.SUBMITTED}),
    CaseStatus.QUEUED: frozenset({CaseStatus.QUEUED, CaseStatus.SUBMITTED}),
    CaseStatus.SUBMITTED: frozenset({CaseStatus.ACKNOWLEDGED}),
    CaseStatus.ACKNOWLEDGED: frozenset({CaseStatus.FOLLOW_UP, CaseStatus.IN_PROGRESS, CaseStatus.RESPONDED, CaseStatus.ESCALATED}),
    CaseStatus.FOLLOW_UP: frozenset({CaseStatus.FOLLOW_UP, CaseStatus.RESPONDED, CaseStatus.ESCALATED}),
    CaseStatus.IN_PROGRESS: frozenset({CaseStatus.FOLLOW_UP, CaseStatus.RESPONDED, CaseStatus.ESCALATED}),
    CaseStatus.RESPONDED: frozenset({CaseStatus.FOLLOW_UP, CaseStatus.RESOLVED, CaseStatus.ESCALATED}),
    CaseStatus.RESOLVED: frozenset({CaseStatus.CLOSED}),
    CaseStatus.ESCALATED: frozenset({CaseStatus.RESPONDED, CaseStatus.CLOSED}),
    CaseStatus.CLOSED: frozenset({CaseStatus.ARCHIVED}),
    CaseStatus.ARCHIVED: frozenset(),
}


def can_transition(current: CaseStatus, target: CaseStatus) -> bool:
    """Return whether a status transition is part of the canonical graph."""
    return target in CASE_STATUS_TRANSITIONS[current]


def require_transition(current: CaseStatus, target: CaseStatus) -> None:
    """Fail closed when a requested status transition is outside the graph."""
    if not can_transition(current, target):
        raise ValueError(
            f"Invalid CivicCase transition: {current.value} -> {target.value}"
        )
