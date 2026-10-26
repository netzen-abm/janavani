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

    assert "feat/canonical-capability-execution-envelope|vercel/install-vercel-web-analytics-6417ji)" in source
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
    assert "count_open_prs_for_branch" in source
    assert "env.BRANCH" in source
    assert "env.REPO" in source
    assert "head=$owner:$branch" not in source
    assert "head=$REPO:$branch" not in source


def test_legacy_retirement_helper_does_not_interpolate_branch_names_into_url() -> None:
    source = (
        ROOT / "scripts" / "retire_legacy_branches.py"
    ).read_text(encoding="utf-8")

    assert 'pulls?state=open&per_page=100&page={page}' in source
    assert 'pr.get("head", {}).get("ref") == branch' in source
    assert 'head=netzen-abm:{branch}' not in source


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
    transition = source.split("retire-canonical-capability-envelope:", 1)[1]
    assert "git rev-list --count" not in transition
    assert "git diff --quiet refs/remotes/origin/main" in transition
    assert "git rev-list --count" in source.split(
        "retire-canonical-capability-envelope:", 1
    )[0]



def test_rejected_analytics_branch_is_path_limited_and_archived_before_retirement() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    retirement = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")

    assert "feat/canonical-capability-execution-envelope|vercel/install-vercel-web-analytics-6417ji)" in ci
    assert "Retirement-only branch; policy files only" in ci
    assert "github.event.pull_request.head.ref == 'vercel/install-vercel-web-analytics-6417ji'" in retirement
    assert "retire-rejected-vercel-analytics:" in retirement
    assert "697ef531d9a02ab9a03b9986efa6b0a633766985" in retirement
    assert "archive/rejected-analytics/" in retirement
    assert "archive/branches/" in retirement
    assert "RETIREMENT VERIFIED" in retirement



def test_backup_restore_uses_postgres16_matched_client_binaries() -> None:
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    section = source.split("name: Prove PostgreSQL backup and restore integrity:", 1)[1].split(
        "name: Prove PostgreSQL service restart durability:", 1
    )[0]

    assert "ancestor=postgres:16" in section
    assert 'docker exec -e PGPASSWORD="$PGPASSWORD" "$container_id"' in section
    assert "pg_dump --username=\"$PGUSER\"" in section
    assert "pg_restore --username=\"$PGUSER\"" in section
    assert "pg_restore --exit-on-error --no-owner --no-privileges --dbname=janavani_restore_test \"$backup_file\"" not in section
