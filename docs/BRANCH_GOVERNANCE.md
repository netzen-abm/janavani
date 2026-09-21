# Janavani Branch Governance

## Active branch budget

Janavani maintains exactly nine intentional long-lived development branch roles:

1. `main` — canonical production-integration/convergence line
2. `integration/canonical-platform` — shared platform convergence
3. `feat/canonical-case-kernel` — canonical Case kernel work
4. `feat/canonical-capability-execution-envelope` — shared execution-context contract
5. `feat/canonical-civic-action-vertical-slice` — end-to-end civic-action slice
6. `feat/canonical-sos-contract` — SOS contract/decomposition work
7. `feat/capability-scoped-consent-agent-enforcement` — capability-scoped consent/agent security
8. `audit/postgres-provider-production-gates` — durable-provider readiness verification
9. `chore/ecosystem-shared-capability-infrastructure` — ecosystem infrastructure convergence

These are the only active development roles. Historical refs outside this set are retirement candidates and must receive no new development.

## Rules

- `main` is the canonical implementation line.
- No new long-lived branch may be created without replacing one of the nine approved roles.
- Do not create version-suffixed generations such as `-v2`, `-v3`, `-final`, or `-clean`.
- Historical branches are evidence sources, not active development lines.
- Before retiring a branch, compare it with `main`, identify unique commits/files, and preserve useful substance on `main` before deletion.
- Never force-move a historical branch merely to simulate deletion.
- A branch is retired only after its useful delta is verified on `main` and the branch ref is actually deleted.
- WebApp, Telegram and future surfaces must consume shared capability/provider infrastructure; surface-specific branches must not introduce duplicate domain implementations.

## Retirement protocol

`AUDIT → EXTRACT → CONVERGE → VERIFY → ARCHIVE EVIDENCE → DELETE REF`

A branch that is fully behind `main`, or whose useful delta is already present on `main`, is a retirement candidate. A divergent branch with unique useful work must be selectively converged rather than blindly merged.

## Enforcement status

CI rejects work from unapproved branch names and the canonical `main` gate requires exactly nine physical remote branch refs.

The repository currently still contains historical refs beyond the nine-role target. Physical branch-ref deletion is an operational GitHub administration step not exposed by the connected mutation surface. Until those refs are actually deleted, the repository is not reported as having nine physical branches.

No historical ref is force-moved as a substitute for deletion.
