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

After approved merge, the archive-first retirement workflow must archive the exact PR branch head, verify the branch tree matches merged `main`, delete the branch, and query GitHub again to prove exactly eight physical refs remain. Until that verification succeeds, report the observed physical count; do not claim eight-ref compliance.

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

## Enforcement status — 13 November 2026

CI allows the eight active branch roles plus the narrowly scoped PR #243 integration exception. The canonical `main` push gate requires exactly eight physical remote branch refs and waits briefly for the post-merge retirement workflow.

The latest live inventory still reports nine physical refs: the eight sanctioned long-lived roles plus `feat/capability-activation-governance`. The exact-eight physical target is not yet met. The seven other development branches have unique deltas relative to `main`; no safe archive-and-delete-only candidate was found in the latest comparison.

A green PR alone does not establish physical branch-budget compliance. After the retirement workflow, independently query the branch list and verify the eight sanctioned refs. The eventual product-release end state is a single `main` branch after all useful work is integrated and release/recovery gates pass.
