from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_branch_budget_excludes_remote_head_symbolic_alias():
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "refs/remotes/origin/" in source
    assert "/^HEAD$/d" in source
    assert 'if [ "$count" -ne 8 ]' in source


def test_branch_allowlist_contains_exactly_eight_active_roles():
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    allowed = {
        "main",
        "integration/canonical-platform",
        "feat/canonical-case-kernel",
        "feat/canonical-civic-action-vertical-slice",
        "feat/canonical-sos-contract",
        "feat/capability-scoped-consent-agent-enforcement",
        "audit/postgres-provider-production-gates",
        "chore/ecosystem-shared-capability-infrastructure",
    }

    assert len(allowed) == 8
    for branch in allowed:
        assert branch in source


def test_retirement_branch_is_not_an_active_role_and_is_path_limited() -> None:
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "feat/canonical-capability-execution-envelope)" in source
    assert "Retirement-only branch" in source
    assert ".github/workflows/security-ci.yml" in source
    assert "docs/BRANCH_GOVERNANCE.md" in source
    assert "docs/MASTER_TASK_CHECKLIST.md" in source
    assert "docs/governance/MASTER_TASK_REGISTER.md" in source
    assert "docs/architecture/SHAREABLE_INFRASTRUCTURE_BOUNDARIES.md" in source
    assert "scripts/retire_legacy_branches.py" in source
    assert "Janavani requires exactly eight physical branch refs" in source


def test_branch_retirement_serializes_mutations_and_scopes_open_pr_lookup() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")

    assert "group: janavani-branch-retirement" in source
    assert 'owner="${repo%%/*}"' in source
    assert 'head=$owner:$branch' in source
    assert 'head=$REPO:$branch' not in source


def test_main_ruleset_required_checks_have_matching_workflow_job_names() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    security = (
        ROOT / ".github" / "workflows" / "security-ci.yml"
    ).read_text(encoding="utf-8")

    assert "name: Python Lint & Test" in ci
    assert "name: Rust Compilation & Clippy" in ci
    assert "name: Secret Leak Check" in security


def test_retirement_workflow_archives_and_verifies_before_deleting() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")

    assert "pull_request:" in source
    assert "github.event.pull_request.merged == true" in source
    assert "archive/branches/" in source
    assert "ARCHIVE VERIFIED" in source
    assert "Retirement-only branch" in source
    assert "ahead_by" not in source  # Compare is performed from fetched Git refs.
    assert "git rev-list --count" in source
    assert "git diff --quiet" in source
