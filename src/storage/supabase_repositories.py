"""Supabase-backed repository boundary for canonical workflow records.

This module deliberately does not pretend that the production schema is
already deployed. It validates configuration and isolates the Supabase client
behind the same repository contracts used by the workflow service.
"""

from __future__ import annotations

from typing import Any

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


class SupabaseConfigurationError(RuntimeError):
    """Raised when the durable repository cannot be safely configured."""


class SupabaseRepositoryBase:
    def __init__(self, client: Any) -> None:
        if client is None:
            raise SupabaseConfigurationError("Supabase client is required")
        self.client = client


class SupabaseCaseRepository(SupabaseRepositoryBase, CaseRepository):
    """Durable Case repository boundary.

    Table/schema mapping is intentionally kept explicit and is not inferred at
    runtime. The adapter remains unavailable until the canonical schema exists.
    """

    table_name = "cases"

    def get(self, case_id: str) -> Case | None:
        raise NotImplementedError("canonical cases schema mapping is not deployed")

    def save(self, case: Case) -> Case:
        raise NotImplementedError("canonical cases schema mapping is not deployed")


class SupabaseEvidenceRepository(SupabaseRepositoryBase, EvidenceRepository):
    table_name = "evidence"

    def save(self, evidence: Evidence) -> Evidence:
        raise NotImplementedError("canonical evidence schema mapping is not deployed")


class SupabaseAuthorityRepository(SupabaseRepositoryBase, AuthorityRepository):
    table_name = "authorities"

    def get(self, authority_id: str) -> Authority | None:
        raise NotImplementedError("canonical authorities schema mapping is not deployed")


class SupabaseSubmissionRepository(SupabaseRepositoryBase, SubmissionRepository):
    table_name = "submissions"

    def get(self, submission_id: str) -> Submission | None:
        raise NotImplementedError("canonical submissions schema mapping is not deployed")

    def save(self, submission: Submission) -> Submission:
        raise NotImplementedError("canonical submissions schema mapping is not deployed")
