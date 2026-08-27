"""Explicit in-process repositories for development and API composition.

These repositories are intentionally scoped to development/testing. They are
not presented as durable production storage.
"""

from __future__ import annotations

from src.application.case_workflow import (
    AuthorityRepository,
    CaseRepository,
    EvidenceRepository,
    SubmissionRepository,
)
from src.domain.authority import Authority
from src.domain.case import Case
from src.domain.evidence import Evidence
from src.domain.submission import Submission


class MemoryCaseRepository(CaseRepository):
    """Store cases in memory for development and tests."""

    def __init__(self) -> None:
        self._items: dict[str, Case] = {}

    def get(self, case_id: str) -> Case | None:
        """Return a case by identifier."""
        return self._items.get(case_id)

    def save(self, case: Case) -> Case:
        """Persist a case in the in-memory store."""
        self._items[case.id] = case
        return case


class MemoryEvidenceRepository(EvidenceRepository):
    """Store evidence in memory for development and tests."""

    def __init__(self) -> None:
        self._items: dict[str, Evidence] = {}

    def save(self, evidence: Evidence) -> Evidence:
        """Persist evidence in the in-memory store."""
        self._items[evidence.evidence_id] = evidence
        return evidence


class MemoryAuthorityRepository(AuthorityRepository):
    """Store authority references in memory for development and tests."""

    def __init__(self, authorities: list[Authority] | None = None) -> None:
        self._items = {
            authority.authority_id: authority
            for authority in authorities or []
        }

    def get(self, authority_id: str) -> Authority | None:
        """Return an authority by identifier."""
        return self._items.get(authority_id)

    def save(self, authority: Authority) -> Authority:
        """Persist an authority in the in-memory store."""
        self._items[authority.authority_id] = authority
        return authority


class MemorySubmissionRepository(SubmissionRepository):
    """Store submissions in memory for development and tests."""

    def __init__(self) -> None:
        self._items: dict[str, Submission] = {}

    def get(self, submission_id: str) -> Submission | None:
        """Return a submission by identifier."""
        return self._items.get(submission_id)

    def save(self, submission: Submission) -> Submission:
        """Persist a submission in the in-memory store."""
        self._items[submission.submission_id] = submission
        return submission
