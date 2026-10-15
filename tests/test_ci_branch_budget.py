from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_physical_branch_budget_uses_canonical_repository_api():
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'repos/${GITHUB_REPOSITORY}/branches?per_page=100' in source
    assert "gh api --paginate" in source
    assert 'if [ "$count" -ne 9 ]' in source


def test_branch_allowlist_contains_exactly_nine_roles():
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    allowed = {
        "main",
        "integration/canonical-platform",
        "feat/canonical-case-kernel",
        "feat/canonical-civic-action-vertical-slice",
        "feat/canonical-capability-execution-envelope",
        "feat/canonical-sos-contract",
        "feat/capability-scoped-consent-agent-enforcement",
        "audit/postgres-provider-production-gates",
        "chore/ecosystem-shared-capability-infrastructure",
    }

    assert len(allowed) == 9
    for branch in allowed:
        assert branch in source
