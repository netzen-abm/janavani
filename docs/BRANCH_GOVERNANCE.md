# Janavani Branch Governance

## Active branch budget

Janavani maintains exactly eight intentional long-lived development branch roles:

1. `main` — canonical production-integration/convergence line
2. `integration/canonical-platform` — shared platform convergence
3. `feat/canonical-case-kernel` — canonical Case kernel work
4. `feat/canonical-civic-action-vertical-slice` — end-to-end civic-action slice
5. `feat/canonical-sos-contract` — SOS contract/decomposition work
6. `feat/capability-scoped-consent-agent-enforcement` — capability-scoped consent/agent security
7. `audit/postgres-provider-production-gates` — durable-provider readiness verification
8. `chore/ecosystem-shared-capability-infrastructure` — ecosystem infrastructure convergence

The branch `feat/canonical-capability-execution-envelope` is a **temporary retirement-only transition ref**, not an active development role. It may carry only the narrow branch-policy and archive-first retirement changes needed to retire itself. The physical inventory remains nine until the post-merge retirement workflow verifies its archive, deletes the ref, and confirms eight physical branches.

## Rules

- `main` is the canonical implementation line.
- No new long-lived branch may be created without replacing one of the eight approved roles.
- Do not create version-suffixed generations such as `-v2`, `-v3`, `-final`, or `-clean`.
- Historical branches are evidence sources, not active development lines.
- Before retiring a branch, compare it with `main`, identify unique commits/files, and preserve useful substance on `main` before deletion.
- Never force-move a historical branch merely to simulate deletion.
- A branch is retired only after its useful delta is verified on `main`, its exact head is archived, the ref is actually deleted, and the live inventory confirms the target count.
- The transition ref `feat/canonical-capability-execution-envelope` is retired only by the guarded post-merge workflow. It must not be deleted manually before its policy PR is merged.
- WebApp, Telegram and future surfaces must consume shared capability/provider infrastructure; surface-specific branches must not introduce duplicate domain implementations.

## Retirement protocol

`AUDIT → EXTRACT → CONVERGE → VERIFY → ARCHIVE EXACT HEAD → DELETE REF → RE-INVENTORY`

A branch that is fully behind `main`, or whose useful delta is already present on `main`, is a retirement candidate. A divergent branch with unique useful work must be selectively converged rather than blindly merged.

## Enforcement status

CI allows the eight active branch roles plus the narrowly scoped transition-ref exception. The canonical `main` push gate requires exactly eight physical remote branch refs and waits briefly for the post-merge retirement workflow before failing, because the transition branch is deleted immediately after the governance PR merges.

The physical count is not considered compliant until GitHub reports exactly eight branch refs. A green PR alone does not establish that the transition ref was deleted. After deletion, query the live branch list and verify the exact eight sanctioned refs.

No historical ref is force-moved as a substitute for deletion. Future retirements must use the archive-first retirement workflow and re-inventory the live refs after deletion.
