"""Canonical persistence composition for the case workflow.

This module builds one coherent repository graph. It does not switch the
application runtime automatically; callers explicitly choose memory or
Supabase mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.application.case_workflow import CaseWorkflowService
from src.storage.case_memory_repository import (
    MemoryAuthorityRepository,
    MemoryCaseRepository,
    MemoryEvidenceRepository,
    MemorySubmissionRepository,
)
from src.storage.relationship_repository import CanonicalRelationshipRepository
from src.storage.resource_repositories import (
    SupabaseAuthorityRepository,
    SupabaseDocumentRepository,
    SupabaseEvidenceRepository,
)
from src.storage.supabase_repositories import SupabaseCaseRepository, SupabaseSubmissionRepository


@dataclass(frozen=True)
class CanonicalPersistence:
    workflow: CaseWorkflowService
    relationships: Any
    documents: Any | None = None


def memory_persistence() -> CanonicalPersistence:
    return CanonicalPersistence(
        workflow=CaseWorkflowService(
            cases=MemoryCaseRepository(),
            evidence=MemoryEvidenceRepository(),
            authorities=MemoryAuthorityRepository(),
            submissions=MemorySubmissionRepository(),
        ),
        relationships=None,
    )


def supabase_persistence(client: Any) -> CanonicalPersistence:
    """Build the durable repository graph without enabling it implicitly."""
    if client is None:
        raise ValueError("Supabase client is required")
    return CanonicalPersistence(
        workflow=CaseWorkflowService(
            cases=SupabaseCaseRepository(client),
            evidence=SupabaseEvidenceRepository(client),
            authorities=SupabaseAuthorityRepository(client),
            submissions=SupabaseSubmissionRepository(client),
        ),
        relationships=CanonicalRelationshipRepository(client),
        documents=SupabaseDocumentRepository(client),
    )
