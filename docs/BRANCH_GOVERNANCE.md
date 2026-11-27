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

The branch `feat/capability-activation-governance` is a separate, time-bounded integration exception for PR #243 only. It is not a ninth long-lived development role and must receive no unrelated work. The exception is extended once, solely to complete the already-open security review and archive-first integration; it expires on 30 November 2026 and will not be extended again. This does not waive the eight-ref physical target.

### PR #243 merge prerequisites

PR #243 changes consent-purpose separation and the deny-by-default activation boundary. Before merge:

- All exact-head CI, Rust, security, architecture, dependency and deployment-preview checks must pass.
- At least one approval must come from a maintainer other than the PR author.
- Review comments/threads requiring changes must be resolved.
- No production submission transport, production activation, database migration or deployment is authorized by the PR.
- The merge must preserve the citizen-controlled Prepare → Review → Approve → Download workflow.

The current `main` ruleset was inspected on 13 November 2026 and reports `required_approving_review_count: 0` and `require_code_owner_review: false`. Therefore GitHub does not currently enforce the independent-approval requirement. Repository administration must configure at least one required approval before this governance PR is merged. A successful CI run or a comment from the PR author is not an independent approval.

After approved merge, the dedicated PR #243 retirement job first verifies that at least one reviewer other than the PR author has a latest `APPROVED` review whose `commit_id` equals the exact branch head. It then checks there are no other open PRs, archives that exact head, verifies the archive and branch ref, compares the full branch tree with merged `main` (not commit ancestry, so squash/rebase is supported), and deletes the ref using an explicit expected-old-SHA lease. A concurrent push makes deletion fail rather than deleting a newer, unarchived head. The job then verifies the expected intermediate inventory: **nine refs** while PR #247 remains open (the eight sanctioned refs plus PR #247's evidence-contract ref). Exactly eight physical refs are expected only after PR #247's own archive-first workflow completes. If approval, open-PR, archive, lease, or tree-parity checks fail, the branch is not deleted. Until live re-inventory confirms eight refs, report the observed physical count; do not claim eight-ref compliance.

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

## Enforcement status — 27 November 2026

The intended active set remains the eight sanctioned branch roles above. A fresh GitHub inventory on 27 November 2026 reports **11 physical refs**:

- Eight sanctioned roles.
- `feat/capability-activation-governance` — PR #243, a temporary, time-limited governance integration branch.
- `docs/environmental-civic-evidence-contract` — PR #247, a documentation-only proposal with unique content.
- `fix/persistence-provider-wiring` — PR #250 is now **closed as superseded, not merged**; its exact branch ref is preserved until the equivalent implementation on PR #226 reaches `main` and the guarded archive-first cleanup runs.

**The exact-eight physical target is NOT met.** A green branch-role check validates the candidate's permitted role or scoped exception; it does not prove the repository-wide physical count. Do not delete any of these three refs manually.

### Verified disposition and required merge sequence

1. **PR #226 first — canonical product convergence.** PR #226 is Draft/open at `8b9ddbf69dd104ef27966d489991dfb3f80b59dd`. Its exact-head CI, Architecture Guard, Security CI, Docker, Dependency Review, Decentralized Capability Verification and preview acceptance all passed on 26 November. It contains the shared provider-wiring changes described by PR #250. It still needs independent review and an explicit release/merge decision; no independent APPROVED review is recorded.
2. **PR #250 is superseded.** PR #250 was closed on 27 November with its branch retained. The four-file provider-wiring delta was compared with PR #226: DSN propagation for consent, submission, authority and document artifacts; the shared artifact provider factory; lazy shared provider graph; and regression tests are represented on the PR #226 candidate. This is not yet a claim that the changes are on `main`.
3. **PR #243 next — consent and governance convergence.** PR #243 is open at `96ccc123ce34834ba13e007107b56938d8be9eb7`. Its observed exact-head checks passed on 25 November, but it has no independent APPROVED review. The repository ruleset was previously observed with zero required approvals, so an external maintainer approval must be obtained and repository protection configured appropriately. The PR's post-merge workflow now has a dedicated `main`-push job that, only after PR #226 is merged, verifies the equivalent provider-wiring implementation on `main`, archives PR #250's exact head `3363ca203e295a1c28bd15b58d1893cd92c5b1b0`, verifies the tag, and deletes the superseded branch. The PR #243 retirement job waits for this archive/deletion before retiring its own branch.
4. **PR #247 last — unique documentation convergence.** PR #247 remains Draft/open and contains the one-off environmental civic evidence product-mapping document. Its dedicated post-merge workflow waits for the exact PR #243 archive/deletion before archiving and deleting its own branch. Do not close it as superseded or delete it without a separately documented archive-first disposition.

Expected physical-ref sequence, after each guarded workflow verifies its own action:

- Current inventory: 11 refs.
- After the PR #250 cleanup: 10 refs.
- After PR #243 retirement: 9 refs while PR #247 remains open.
- After PR #247 retirement: exactly the eight sanctioned refs.

The final step must query GitHub and verify the exact eight names, not merely count eight arbitrary branches.

### Retirement safeguards

- The PR #250 cleanup is triggered on a `main` push, requires PR #226 to be merged, requires PR #250 closed without merge, checks the exact expected branch head and zero open PR references, verifies the provider-wiring implementation on `main`, creates/verifies the archive tag, then deletes and rechecks the ref.
- PR #243 retirement requires an independent reviewer approval on the exact merged PR head and waits for the PR #250 tag/ref state to be correct before it can finish.
- PR #247 retirement is owned by its own close-event job. PR #243 must not delete the evidence-contract ref as a shortcut.
- Manual retirement must not bypass any of the dedicated transition jobs.
- A failed check preserves the ref. No force-move is used to simulate deletion.

The eventual product-ready end state remains a single `main` branch, only after all useful work is integrated and product, recovery, security and operational acceptance gates pass.
