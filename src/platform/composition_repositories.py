"""Provider-neutral repository composition for Janavani surfaces."""
from __future__ import annotations

import os
from src.core.authority import AuthorityRepository
from src.core.evidence import EvidenceRepository
from src.core.submission import SubmissionRepository
from src.storage.provider_composition import ProviderComposition
from src.storage.repositories.accountability_feedback_provider import create_accountability_feedback_repository as create_feedback_repository
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.consent import ConsentRepository
from src.storage.repositories.consent_provider import create_consent_repository as create_consent_repository_for_provider
from src.storage.repositories.document_review import DocumentReviewRepository
from src.storage.repositories.document_review_provider import create_document_review_repository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.external_channel_provider import create_external_channel_repository
from src.storage.repositories.obligation import AuthorityBackedObligationResolver
from src.storage.repositories.provider import create_civic_case_repository
from src.storage.repositories.responsibility import AuthorityBackedResponsibilityResolver
from src.identity.linking import ExternalIdentityLinkRepository, InMemoryExternalIdentityLinkRepository, PostgresExternalIdentityLinkRepository
from src.storage.repositories.submission_provider import create_submission_repository as create_submission_repository_for_provider

def create_provider_composition() -> ProviderComposition:
    return ProviderComposition.from_environment()

def create_case_repository(*, provider_composition: ProviderComposition | None = None) -> CivicCaseRepository:
    return create_civic_case_repository(composition=provider_composition or create_provider_composition())

def create_consent_repository(*, provider_composition: ProviderComposition | None = None) -> ConsentRepository:
    composition = provider_composition or create_provider_composition()
    return create_consent_repository_for_provider(provider=composition.provider_for("consent"))

def create_submission_repository(*, provider_composition: ProviderComposition | None = None) -> SubmissionRepository:
    composition = provider_composition or create_provider_composition()
    return create_submission_repository_for_provider(provider=composition.provider_for("submission"))

def create_document_review_repository_for_platform(*, provider_composition: ProviderComposition | None = None) -> DocumentReviewRepository:
    return create_document_review_repository(provider_composition=provider_composition or create_provider_composition())

def create_accountability_feedback_repository(*, provider_composition: ProviderComposition | None = None, path=None):
    composition = provider_composition or create_provider_composition()
    return create_feedback_repository(composition=composition, path=path)

def create_external_channel_repository_for_platform(*, provider_composition: ProviderComposition | None = None):
    return create_external_channel_repository(composition=provider_composition or create_provider_composition())

def create_identity_link_repository(*, provider_composition: ProviderComposition | None = None) -> ExternalIdentityLinkRepository:
    """Select the shared identity-link provider at the composition boundary."""
    composition = provider_composition or create_provider_composition()
    if composition.provider_for("external_identity_links") == "postgres":
        dsn = os.getenv("JANAVANI_POSTGRES_DSN")
        if not dsn:
            raise ValueError("JANAVANI_POSTGRES_DSN is required for PostgreSQL identity persistence")

        def connect():
            try:
                import psycopg
            except ImportError as exc:
                raise RuntimeError("Psycopg 3 is required for PostgreSQL identity persistence") from exc
            return psycopg.connect(dsn)

        return PostgresExternalIdentityLinkRepository(connect)
    return InMemoryExternalIdentityLinkRepository()

def create_authority_repository() -> AuthorityRepository:
    return CsvAuthorityRepository()

def create_development_authority_repository() -> AuthorityRepository:
    return InMemoryAuthorityRepository()

def create_development_evidence_repository() -> EvidenceRepository:
    return InMemoryEvidenceRepository()

def create_responsibility_resolver(authority_repository: AuthorityRepository):
    return AuthorityBackedResponsibilityResolver(authority_repository)

def create_obligation_resolver(authority_repository: AuthorityRepository, records: dict[str, list[dict[str, object]]] | None = None):
    return AuthorityBackedObligationResolver(records or {})
