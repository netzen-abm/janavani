"""Repository contracts and canonical persistence providers."""

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
from src.storage.repositories.postgres_civic_case import (
    PostgresCivicCaseConcurrencyError,
    PostgresCivicCasePersistenceError,
    PostgresCivicCaseRepository,
)
from src.storage.repositories.provider import (
    CivicCaseProviderConfigurationError,
    SUPPORTED_PROVIDERS,
    create_civic_case_repository,
)
from src.storage.repositories.sqlite_document_artifact import (
    SqliteDocumentArtifactRepository,
)
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
    "InMemoryEvidenceRepository",
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
