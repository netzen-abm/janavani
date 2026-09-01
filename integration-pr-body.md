Purpose
Consolidate existing architecture/security/runtime/case PRs into one integration branch for controlled verification and conflict resolution before merging to main.

Included PRs (merge order inside this integration PR)
Wave 0 — Governance
- PR #33 — docs: architecture authority and truthful verification model

Wave 1 — Privacy & Auth
- PR #25 — security: enforce admin zero-access privacy boundary
- PR #40 — security: harden authentication and authorization boundary

Wave 2 — Case & Storage
- PR #29 — feat: establish shared civic case lifecycle contract
- PR #36 — feat: establish canonical case storage boundary
- PR #38 — feat: harden canonical case workflow kernel

Wave 3 — Runtime / CI / Dependencies
- PR #31 — fix: consolidate runtime authority and CI validation
- PR #39 — chore: converge canonical runtime and dependency cleanup
- PR #41 — fix(ci): align root dependencies with canonical test suite

PR #42 (external head: savetigerfirst/my-first-fix)
- NOT INCLUDED — author must retarget to canonical dependency contract; do not merge as-is.

Acceptance criteria (must pass on integration branch)
- Canonical CI (ci.yml) green: smoke tests + run_all_tests.sh
- Admin-zero-access tests (PR#25) pass
- Auth boundary tests (PR#40) pass
- Case contract tests (PR#29/#36/#38) pass
- No privacy/PII regressions
- Resolve all merge conflicts with documented rationale

Rollback plan
- Revert last merge commit on integration branch and re-run tests.
- Keep fix commits small; avoid force-pushing main.

Audit evidence
- For each included PR list files consumed and conflict resolutions in the integration PR description.
