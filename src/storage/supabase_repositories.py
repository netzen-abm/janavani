"""Supabase repositories for the canonical workflow."""

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
from src.storage.hydration import case_from_row, submission_from_row
from src.storage.serialization import case_row, submission_row


class SupabaseConfigurationError(RuntimeError):
    """Raised when the durable repository cannot be safely configured."""


class SupabaseRepositoryBase:
    """Common boundary around an already-created Supabase client."""

    def __init__(self, client: Any) -> None:
        if client is None:
            raise SupabaseConfigurationError("Supabase client is required")
        self.client = client


class SupabaseCaseRepository(SupabaseRepositoryBase, CaseRepository):
    """Persist and retrieve canonical Case rows."""

    table_name = "cases"

    def get(self, case_id: str) -> Case | None:
        """Return a Case by identifier."""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("id", case_id)
            .limit(1)
            .execute()
        )
        rows = getattr(response, "data", None) or []
        return case_from_row(rows[0]) if rows else None

    def save(self, case: Case) -> Case:
        """Upsert and return a canonical Case."""
        response = self.client.table(self.table_name).upsert(case_row(case)).execute()
        rows = getattr(response, "data", None) or []
        return case_from_row(rows[0]) if rows else case


class SupabaseSubmissionRepository(SupabaseRepositoryBase, SubmissionRepository):
    """Persist and retrieve canonical Submission rows."""

    table_name = "submissions"

    def get(self, submission_id: str) -> Submission | None:
        """Return a Submission by identifier."""
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("submission_id", submission_id)
            .limit(1)
            .execute()
        )
        rows = getattr(response, "data", None) or []
        return submission_from_row(rows[0]) if rows else None

    def save(self, submission: Submission) -> Submission:
        """Upsert and return a canonical Submission."""
        response = (
            self.client.table(self.table_name)
            .upsert(submission_row(submission))
            .execute()
        )
        rows = getattr(response, "data", None) or []
        return submission_from_row(rows[0]) if rows else submission


class SupabaseEvidenceRepository(SupabaseRepositoryBase, EvidenceRepository):
    """Evidence adapter remains gated until relationship writes are transactional."""

    table_name = "evidence"

    def save(self, evidence: Evidence) -> Evidence:
        """Reject use until evidence persistence is transactionally composed."""
        raise NotImplementedError(
            "evidence persistence requires transactional case relationship handling"
        )


class SupabaseAuthorityRepository(SupabaseRepositoryBase, AuthorityRepository):
    """Authority lookup remains gated pending canonical hydration integration."""

    table_name = "authorities"

    def get(self, authority_id: str) -> Authority | None:
        """Reject lookup until the canonical authority path is enabled."""
        raise NotImplementedError("authority hydration integration is pending")
