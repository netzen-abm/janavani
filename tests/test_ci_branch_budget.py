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

    assert "group: janavani-branch-retirement-" in source
    assert "github.event.pull_request.number" in source
    assert "count_open_prs_for_branch" in source
    assert "env.BRANCH" in source
    assert "env.REPO" in source
    assert "head=$owner:$branch" not in source
    assert "head=$REPO:$branch" not in source

    manual = source.split("  retire:", 1)[1].split(
        "  retire-consent-capability-governance:", 1
    )[0]
    assert 'remaining" != "$expected"' in manual
    assert 'printf \'%s\\n\' "${sanctioned[@]}"' in manual
    assert 'remaining_count="$(printf \'%s\\n\' "$remaining" | wc -l | tr -d \' \')"' in manual
    assert "exact sanctioned inventory" in manual


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
    assert "github.event_name == 'push'" in retirement
    assert "github.ref == 'refs/heads/main'" in retirement
    assert "retire-rejected-vercel-analytics:" in retirement
    assert "697ef531d9a02ab9a03b9986efa6b0a633766985" in retirement
    assert "archive/rejected-analytics/" in retirement
    assert "archive/branches/" in retirement
    assert "RETIREMENT VERIFIED" in retirement
    assert "permissions:" in retirement
    assert "  contents: write" in retirement
    assert "  pull-requests: read" in retirement
    assert 'git push --porcelain --force-with-lease="refs/heads/$branch:$head_sha" origin ":refs/heads/$branch"' in retirement



def test_backup_restore_uses_postgres16_matched_client_binaries() -> None:
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    section = source.split("name: Prove PostgreSQL backup and restore integrity", 1)[1].split(
        "name: Prove PostgreSQL service restart durability", 1
    )[0]

    assert "ancestor=postgres:16" in section
    assert 'docker exec -e PGPASSWORD="$PGPASSWORD" "$container_id"' in section
    assert "pg_dump --username=\"$PGUSER\"" in section
    assert "pg_restore --username=\"$PGUSER\"" in section
    assert "pg_restore --exit-on-error --no-owner --no-privileges --dbname=janavani_restore_test \"$backup_file\"" not in section


def test_consent_governance_is_a_time_limited_integration_exception() -> None:
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "feat/capability-activation-governance)" in source
    assert 'EVENT_NAME" = "pull_request"' in source
    assert 'github.event.pull_request.number }}" != "243"' in source
    assert 'EVENT_NAME" = "push"' in source
    assert '.number == 243' in source
    assert 'pulls?state=open&per_page=100' in source
    assert '.head.ref == env.BRANCH' in source
    assert '.head.repo.full_name == env.REPO' in source
    assert '.base.ref == "main"' in source
    assert 'expiry="2026-11-30"' in source
    assert "Temporary consent-governance integration exception expired" in source
    assert ".number == 243" in source and ".number == 247" in source


def test_manual_retirement_uses_real_newlines_for_exact_inventory() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    section = source.split("  retire:", 1)[1].split(
        "  retire-consent-capability-governance:", 1
    )[0]
    assert 'expected="$(printf \'%s\\n\' "${sanctioned[@]}" | sort)"' in section
    assert "printf 'Actual refs:\\n%s\\nExpected refs:\\n%s\\n'" in section


def test_consent_governance_branch_is_archived_before_post_merge_deletion() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    section = source.split("retire-consent-capability-governance:", 1)[1].split(
        "retire-canonical-capability-envelope:", 1
    )[0]

    assert "github.event.pull_request.merged == true" in section
    assert "feat/capability-activation-governance" in section
    assert "expected_pr_head_sha=\"\u0024{{ github.event.pull_request.head.sha }}\"" in section
    assert 'if [ "$head_sha" != "$expected_pr_head_sha" ]' in section
    assert "archive/branches/" in section
    assert "Consent archive does not preserve the exact merged PR event head." in section
    assert 'branch_http="$(curl -sS' in section
    assert 'case "$branch_http" in' in section
    assert '            404)' in section
    assert 'refs/pull/$pr_number/head:$git_ref' in section
    assert 'if [ "$(git rev-parse "$git_ref")" != "$expected_pr_head_sha" ]; then' in section
    assert '-v expected="$expected_pr_head_sha"' in section
    assert 'if [ "$archive_sha" != "$expected_pr_head_sha" ]' in section
    assert '[ "$current_sha" != "$expected_pr_head_sha" ]' in section
    assert "branch_present_at_start=true" in section
    assert "branch_present_at_start=false" in section
    assert "Consent branch was already absent after exact-head archive verification" in section
    assert "Consent branch was recreated after the initial absence check" in section
    assert "Consent branch moved after archive verification; preserving it." in section
    assert 'git push --porcelain --force-with-lease="refs/heads/$branch:$expected_pr_head_sha" origin ":refs/heads/$branch"' in section
    assert 'if [ "$remaining" -ne 8 ]' not in section
    assert 'docs/environmental-civic-evidence-contract' in section
    assert 'if [ "$evidence_state" = "open" ]' in section
    assert "PR #247's own close-event workflow is the sole owner of its ref." in section
    assert "expected_nine=" in section
    assert "expected_eight=" in section
    assert "PR #247 remains open and its branch is preserved." in section
    assert "PR #247's workflow has retired its own ref" in section
    assert 'retire-environmental-civic-evidence-contract:' in source
    assert 'consent_archive" != "$consent_head"' in source
    assert 'if [ "$remaining" != "$expected" ]' in section
    assert 'pulls/$pr_number/reviews?per_page=100' in section
    assert '.commit_id' in section
    assert 'latest_state[login] == "APPROVED"' in section
    assert 'latest_commit[login] == expected' in section
    assert 'login != author' in section
    assert 'no current-head approval from a reviewer other than its author' in section


def test_consent_retirement_leaves_pr247_ref_to_its_own_workflow() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    consent = source.split("retire-consent-capability-governance:", 1)[1].split(
        "retire-environmental-civic-evidence-contract:", 1
    )[0]
    evidence = source.split("retire-environmental-civic-evidence-contract:", 1)[1].split(
        "retire-canonical-capability-envelope:", 1
    )[0]

    assert "PR #247's own close-event workflow is the sole owner of its ref." in consent
    assert "current_evidence_sha=" in consent
    assert "archive/branches/docs/environmental-civic-evidence-contract" in consent
    assert "expected_nine=" in consent
    assert "expected_eight=" in consent
    assert 'gh api --method DELETE "repos/$REPO/git/refs/heads/$evidence_branch"' not in consent
    assert 'git push --porcelain --force-with-lease="refs/heads/$branch:$expected_pr_head_sha" origin ":refs/heads/$branch"' in consent
    assert 'git push --porcelain --force-with-lease="refs/heads/$branch:$expected_pr_head_sha" origin ":refs/heads/$branch"' in evidence
    assert 'consent_ready=true' in evidence
    assert 'if [ "$remaining" != "$expected" ]' in evidence


def test_environmental_evidence_retirement_waits_for_consent_governance_and_verifies_eight_refs() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    section = source.split("retire-environmental-civic-evidence-contract:", 1)[1].split(
        "retire-canonical-capability-envelope:", 1
    )[0]

    assert "github.event.pull_request.merged == true" in section
    assert "docs/environmental-civic-evidence-contract" in section
    assert "Waiting for PR #243 merge and exact-head archive-first retirement" in section
    assert "for attempt in $(seq 1 60)" in section
    assert 'sleep 10' in section
    assert "did not complete merge and exact-head archive retirement within 10 minutes" in section
    assert 'consent_tag="archive/branches/feat/capability-activation-governance"' in section
    assert 'consent_archive" != "$consent_head"' in section
    assert 'Retirement held: PR #243 archive is missing or does not match its merged head.' in section
    assert "archive/branches/" in section
    assert 'git push --porcelain --force-with-lease="refs/heads/$branch:$expected_pr_head_sha" origin ":refs/heads/$branch"' in section
    assert 'if [ "$remaining" != "$expected" ]' in section
    assert "RETIREMENT VERIFIED" in section


def test_environmental_evidence_retirement_is_bound_to_closed_pr_head() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    section = source.split("retire-environmental-civic-evidence-contract:", 1)[1].split(
        "retire-canonical-capability-envelope:", 1
    )[0]

    assert 'expected_pr_head_sha="${{ github.event.pull_request.head.sha }}"' in section
    assert 'if [ "$head_sha" != "$expected_pr_head_sha" ]; then' in section
    assert 'if [ "$(git rev-parse "$git_ref")" != "$expected_pr_head_sha" ]' in section
    assert 'if [ "$archive_sha" != "$expected_pr_head_sha" ]' in section
    assert '[ "$current_sha" != "$expected_pr_head_sha" ]' in section
    assert 'evidence_api_head" != "$expected_pr_head_sha"' in section


def test_manual_retirement_never_bypasses_specialized_transition_gates():
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    manual = source.split("  retire:", 1)[1].split(
        "  retire-consent-capability-governance:", 1
    )[0]

    assert "transition_only=(" in manual
    assert '"feat/capability-activation-governance"' in manual
    assert '"docs/environmental-civic-evidence-contract"' in manual
    assert "is_transition_only \"$branch\"" in manual
    assert "deleted only by its dedicated approval- and archive-gated workflow" in manual


def test_branch_retirement_uses_independent_pull_request_concurrency_slots():
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")

    assert "group: janavani-branch-retirement-${{ github.event_name" in source
    assert "github.event.pull_request.number" in source
    assert "'manual'" in source
    assert "cancel-in-progress: false" in source


def test_environmental_evidence_branch_is_a_narrow_documentation_transition() -> None:
    source = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    section = source.split("docs/environmental-civic-evidence-contract)", 1)[1].split(
        "main|integration/canonical-platform|feat/canonical-case-kernel)", 1
    )[0]

    assert 'github.event.pull_request.number' in section
    assert '"247"' in section
    assert 'github.event.pull_request.base.ref' in section
    assert '"main"' in section
    assert 'EVENT_NAME" = "push"' in section
    assert '.number == 247' in section
    assert 'git diff --no-renames --name-only' in section
    assert 'expiry="2026-11-30"' in section
    assert 'docs/architecture/ENVIRONMENTAL_CIVIC_EVIDENCE_PRODUCT_MAPPING.md' in section
    assert "Documentation-only transition" in section


def test_superseded_provider_ref_is_retired_only_after_pr226_convergence() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    section = source.split(
        "  retire-superseded-persistence-provider-wiring:", 1
    )[1].split("  retire-consent-capability-governance:", 1)[0]

    assert "github.event_name == 'push'" in section
    assert "github.ref == 'refs/heads/main'" in section
    assert "repos/$REPO/pulls/226" in section
    assert ".merged_at // empty" in section
    assert "Cannot retire PR #250's ref before PR #226 is merged." in section
    assert "repos/$REPO/pulls/250" in section
    assert "fix/persistence-provider-wiring" in section
    assert "3363ca203e295a1c28bd15b58d1893cd92c5b1b0" in section
    assert "test_shared_provider_wiring.py" in section
    assert "dsn=os.getenv(\"JANAVANI_POSTGRES_DSN\")" in section
    assert "archive/branches/$branch" in section
    assert 'git push --porcelain --force-with-lease="refs/heads/$branch:$expected_head" origin ":refs/heads/$branch"' in section
    assert "ARCHIVE VERIFIED" in section
    assert "DELETED AFTER VERIFIED ARCHIVE" in section


def test_consent_retirement_waits_for_superseded_provider_archive_and_deletion() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    section = source.split(
        "  retire-consent-capability-governance:", 1
    )[1].split("  retire-environmental-civic-evidence-contract:", 1)[0]

    assert "PR #226 must be merged before PR #243 branch retirement." in section
    assert 'provider_branch="fix/persistence-provider-wiring"' in section
    assert 'provider_head="3363ca203e295a1c28bd15b58d1893cd92c5b1b0"' in section
    assert 'provider_tag="archive/branches/$provider_branch"' in section
    assert "for attempt in $(seq 1 60)" in section
    assert 'if [ "$provider_retired" != true ]' in section
    assert "PR #250 ref was not retired after PR #226 convergence" in section




def test_branch_retirement_uses_exact_head_leases_and_never_unconditional_delete() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    assert "gh api --method DELETE" not in source
    assert source.count("git push --porcelain --force-with-lease=") == 6
    assert '--force-with-lease="refs/heads/$branch:$expected_head"' in source
    assert '--force-with-lease="refs/heads/$branch:$expected_pr_head_sha"' in source
    assert '--force-with-lease="refs/heads/$branch:$head_sha"' in source


def test_branch_retirement_waiters_fail_closed_on_non_404_ref_errors() -> None:
    source = (
        ROOT / ".github" / "workflows" / "branch-retirement.yml"
    ).read_text(encoding="utf-8")
    assert 'case "$provider_http" in' in source
    assert 'case "$consent_ref_http" in' in source
    assert 'case "$archive_http" in' in source
    assert 'case "$consent_archive_http" in' in source
