"""Repository contracts and canonical persistence providers."""

from src.storage.repositories.artifact_provider import (
    DocumentArtifactProviderConfigurationError,
    SUPPORTED_ARTIFACT_PROVIDERS,
    create_document_artifact_repository,
)
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.authority_csv import CsvAuthorityRepository
from src.storage.repositories.civic_case import (
    CivicCaseRepository,
    InMemoryCivicCaseRepository,
)
from src.storage.repositories.document_artifact import (
    DocumentArtifactRepository,
    InMemoryDocumentArtifactRepository,
)
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.storage.repositories.evidence_provider import (
    EvidenceProviderConfigurationError,
    SUPPORTED_EVIDENCE_PROVIDERS,
    create_evidence_repository,
)
from src.storage.repositories.postgres_civic_case import (
    PostgresCivicCaseConcurrencyError,
    PostgresCivicCasePersistenceError,
    PostgresCivicCaseRepository,
)
from src.storage.repositories.postgres_document_artifact import (
    PostgresDocumentArtifactRepository,
)
from src.storage.repositories.postgres_evidence import PostgresEvidenceRepository
from src.storage.repositories.provider import (
    CivicCaseProviderConfigurationError,
    SUPPORTED_PROVIDERS,
    create_civic_case_repository,
)
from src.storage.repositories.sqlite_document_artifact import (
    SqliteDocumentArtifactRepository,
)
from src.storage.repositories.sqlite_evidence import SqliteEvidenceRepository
from src.storage.repositories.supabase_civic_case import (
    CivicCaseConcurrencyError,
    CivicCasePersistenceError,
    SupabaseCivicCaseRepository,
)

__all__ = [
    "CivicCaseRepository",
    "InMemoryCivicCaseRepository",
    "InMemoryAuthorityRepository",
    "CsvAuthorityRepository",
    "DocumentArtifactRepository",
    "InMemoryDocumentArtifactRepository",
    "SqliteDocumentArtifactRepository",
    "PostgresDocumentArtifactRepository",
    "create_document_artifact_repository",
    "SUPPORTED_ARTIFACT_PROVIDERS",
    "DocumentArtifactProviderConfigurationError",
    "InMemoryEvidenceRepository",
    "SqliteEvidenceRepository",
    "PostgresEvidenceRepository",
    "create_evidence_repository",
    "SUPPORTED_EVIDENCE_PROVIDERS",
    "EvidenceProviderConfigurationError",
    "CivicCaseConcurrencyError",
    "CivicCasePersistenceError",
    "SupabaseCivicCaseRepository",
    "PostgresCivicCaseConcurrencyError",
    "PostgresCivicCasePersistenceError",
    "PostgresCivicCaseRepository",
    "CivicCaseProviderConfigurationError",
    "SUPPORTED_PROVIDERS",
    "create_civic_case_repository",
]
