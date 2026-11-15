# Janavani Branch Governance

## Active branch budget

Janavani maintains exactly eight intentional long-lived development branch roles:

1. `main` — canonical production-integration and eventual convergence line.
2. `integration/canonical-platform` — shared platform convergence.
3. `feat/canonical-case-kernel` — canonical Case kernel.
4. `feat/canonical-civic-action-vertical-slice` — end-to-end civic-action slice.
5. `feat/canonical-sos-contract` — SOS contract and decomposition.
6. `feat/capability-scoped-consent-agent-enforcement` — capability-scoped consent and agent security.
7. `audit/postgres-provider-production-gates` — durable-provider readiness.
8. `chore/ecosystem-shared-capability-infrastructure` — ecosystem infrastructure convergence.

The branch `feat/capability-activation-governance` is a separate, time-bounded integration exception for PR #243 only. It is not a ninth long-lived development role and must receive no unrelated work. The exception expires on 17 November 2026; it must not be extended merely to avoid resolving the branch count.

### PR #243 merge prerequisites

PR #243 changes consent-purpose separation and the deny-by-default activation boundary. Before merge:

- All exact-head CI, Rust, security, architecture, dependency and deployment-preview checks must pass.
- At least one approval must come from a maintainer other than the PR author.
- Review comments/threads requiring changes must be resolved.
- No production submission transport, production activation, database migration or deployment is authorized by the PR.
- The merge must preserve the citizen-controlled Prepare → Review → Approve → Download workflow.

The current `main` ruleset was inspected on 13 November 2026 and reports `required_approving_review_count: 0` and `require_code_owner_review: false`. Therefore GitHub does not currently enforce the independent-approval requirement. Repository administration must configure at least one required approval before this governance PR is merged. A successful CI run or a comment from the PR author is not an independent approval.

After approved merge, the dedicated PR #243 retirement job first verifies that at least one reviewer other than the PR author has a latest `APPROVED` review whose `commit_id` equals the exact branch head. It then checks there are no other open PRs, archives that exact head, verifies the archive and branch ref, compares the full branch tree with merged `main` (not commit ancestry, so squash/rebase is supported), deletes the ref, and queries GitHub again to prove exactly eight physical refs remain. If the approval, open-PR, archive, or tree-parity check fails, the branch is not deleted. Until live re-inventory confirms eight refs, report the observed physical count; do not claim eight-ref compliance.

## Rules

- `main` is the canonical implementation and production-integration line.
- No new long-lived branch may be created without replacing one of the eight approved roles.
- Do not create version-suffixed generations such as `-v2`, `-v3`, `-final`, or `-clean`.
- Historical branches and archive tags are evidence sources, not active development lines.
- Before retiring a branch, compare it with `main`, identify unique commits/files and preserve useful substance on `main`.
- Never force-move a historical branch merely to simulate deletion.
- A branch is retired only after its useful delta is verified on `main`, its exact head is archived, the ref is actually deleted, and the live inventory confirms the target count.
- WebApp, Telegram and future surfaces must consume shared capability/provider infrastructure; surface-specific branches must not introduce duplicate domain implementations.

## Retirement protocol

`AUDIT → EXTRACT → CONVERGE → VERIFY → ARCHIVE EXACT HEAD → DELETE REF → RE-INVENTORY`

A branch fully contained in `main`, or with a tree identical to `main`, may be a retirement candidate only after checking open PR dependencies and preserving an exact archive. A divergent branch with unique useful work must be selectively converged rather than blindly deleted or merged.

## Historical retirement record

The former temporary transition branch `feat/canonical-capability-execution-envelope` is no longer a physical branch. Its exact historical head is preserved by tag `archive/branches/feat/canonical-capability-execution-envelope` at commit `d036839730968771e0db6d043eb2c85ad9531a88`. It is historical evidence only and must not be recreated as an active role.

## Enforcement status — 15 November 2026

The eight sanctioned long-lived branch roles remain the intended policy. Two temporary, PR-scoped integration refs are currently open in addition to those roles:

- `feat/capability-activation-governance` — PR #243, a time-limited security/consent integration branch. Its exception expires on 17 November 2026 and its post-merge workflow archives the exact head before deleting the ref.
- `docs/environmental-civic-evidence-contract` — PR #247, a one-off documentation-only product-mapping proposal. It is not a ninth long-lived role and must remain until its unique document is either integrated or explicitly archived.

**Latest GitHub physical inventory: 10 refs (8 sanctioned roles + 2 open PR refs). The exact-eight physical target is NOT met.** A successful PR #243 branch-budget job validates its scoped PR exception; it does not prove physical branch-count compliance.

### Two-stage temporary-ref retirement

The two one-off PR refs are not interchangeable and must not be deleted simply to meet the count.

- When PR #243 merges first, its post-merge job archives/deletes `feat/capability-activation-governance`. If PR #247 remains open, the job verifies that the remaining inventory is exactly the eight sanctioned roles plus `docs/environmental-civic-evidence-contract` (nine refs), then reports that the final retirement is pending.
- When PR #247 subsequently merges, its dedicated post-merge job first verifies that PR #243's ref has been retired, then archives/deletes the evidence-contract ref and asserts the exact eight sanctioned branch names.
- If PR #247 merged before PR #243, the PR #243 retirement job verifies and retires both temporary refs after the consent branch is archived.
- If PR #247 closes without merge, preserve its unique document branch and halt automatic deletion; make an explicit archive-first disposition before any manual retirement.

This avoids a false failing "exactly eight" assertion after the first merge and prevents either unique PR payload from being discarded.

Do not delete either PR ref before its unique work is incorporated or archived. After each merge, archive the exact head, verify the archive, delete the corresponding ref through a guarded retirement process, and query GitHub again. Do not claim the eight-ref target until a fresh physical inventory returns exactly the eight sanctioned names.

The eventual product-release end state remains a single `main` branch, after all useful work is integrated and product, recovery, security and operational acceptance gates pass.
