"""Provider-local exception contracts for PostgreSQL CivicCase persistence."""
class PostgresCivicCasePersistenceError(RuntimeError):
    """Raised when PostgreSQL Civic Case persistence fails."""

class PostgresCivicCaseConcurrencyError(PostgresCivicCasePersistenceError):
    """Raised when optimistic concurrency detects a stale case version."""
