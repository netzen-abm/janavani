"""Contracts and errors for the PostgreSQL submission provider."""
class PostgresSubmissionPersistenceError(RuntimeError):
    """Raised when PostgreSQL submission persistence fails."""

class PostgresSubmissionConcurrencyError(PostgresSubmissionPersistenceError):
    """Raised when optimistic submission concurrency detects a stale version."""

class PostgresSubmissionIdempotencyConflictError(PostgresSubmissionPersistenceError):
    """Raised when an idempotency key is reused for another operation."""
