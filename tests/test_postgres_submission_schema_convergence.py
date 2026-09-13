from src.storage.repositories.postgres_submission import PostgresSubmissionRepository


def test_submission_initializer_matches_canonical_schema_contract():
    # The compatibility initializer is intentionally inspected as source text:
    # production schema ownership remains with the checked-in migration.
    import inspect

    source = inspect.getsource(PostgresSubmissionRepository._initialize)
    assert "case_id TEXT NOT NULL REFERENCES civic_cases(case_id)" in source
    assert "attempted_at TIMESTAMPTZ" in source
    assert "submitted_at TIMESTAMPTZ" in source
    assert "acknowledged_at TIMESTAMPTZ" in source
    assert "version BIGINT NOT NULL DEFAULT 1" in source
    assert "civic_case_submissions_case_attempted_idx" in source
    assert "civic_case_submissions_destination_idx" in source
