# Janavani Branch Governance

## Active branch budget

Janavani maintains exactly nine active development branch roles:

1. `main` — canonical convergence line
2. `develop/v0.2` — integration/development role
3. `integration/canonical-platform` — platform convergence
4. `integration/case-main-prep` — Case convergence
5. `integration/telegram-consent-convergence-main-v2` — Telegram convergence
6. `feat/product-vertical-slice-convergence` — end-to-end product slice
7. `feat/webapp-authority-evidence-vertical-slice` — WebApp vertical slice
8. `test/authorization-negative-matrix-2026-09` — security verification
9. `security/auth-boundary-hardening` — authorization hardening

## Rules

- `main` is the canonical implementation line.
- No new long-lived branch may be created without replacing one of the nine approved roles.
- Do not create version-suffixed generations such as `-v2`, `-v3`, `-final`, or `-clean`.
- Historical branches are evidence sources, not active development lines.
- Before retiring a branch, compare it with `main), identify unique commits/files, and preserve useful substance on `main) before deletion.
- Never force-move a historical branch merely to simulate deletion.
- A branch is retired only after its useful delta is verified on `main` and the branch ref is actually deleted.
- WebApp and Telegram must consume shared capability/provider infrastructure; surface-specific branches must not introduce duplicate domain implementations.

## Enforcement status

The nine names above are the only authorized active development roles. CI enforcement rejects work from unapproved branch names. Historical refs outside this set are retirement candidates and must receive no new development.

Physical ref deletion remains an operational prerequisite for declaring the repository at exactly nine physical branches; the connected GitHub mutation surface currently exposes no branch-delete operation, so no ref is force-moved or falsely treated as deleted.

## Current cleanup status

The repository currently contains historical refs beyond the nine active roles. The connected GitHub automation used for repository maintenance does not expose a branch-ref deletion mutation. Until an authorized ref-deletion capability is available, those refs must be treated as frozen historical evidence and must not receive new development.

The CI branch-budget gate rejects future work from branches outside the nine approved roles.
