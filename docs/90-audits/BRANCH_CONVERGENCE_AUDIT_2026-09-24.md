# Branch Convergence Audit — 2026-09-24

## Objective

Maintain exactly nine active branches while extracting useful architectural work
into `main` without force-merging stale generations.

## Current physical branch count

**9 — compliant.**

Sanctioned branches:

1. `main`
2. `integration/canonical-platform`
3. `feat/canonical-case-kernel`
4. `feat/canonical-capability-execution-envelope`
5. `feat/canonical-civic-action-vertical-slice`
6. `feat/canonical-sos-contract`
7. `feat/capability-scoped-consent-agent-enforcement`
8. `audit/postgres-provider-production-gates`
9. `chore/ecosystem-shared-capability-infrastructure`

No additional physical branch refs are permitted.

## Convergence decisions

### `feat/canonical-civic-action-vertical-slice`

Compared with current `main`: 10 unique commits.

Unique historical files include the canonical civic-action vertical slice,
composition changes, and tests. The current `main` already contains the
canonical vertical slice and has evolved it further, including document review,
artifact generation, verified external channels, submission gating, and shared
surface composition.

**Decision:** do not merge the branch wholesale. Treat it as historical
evidence/source material. Preserve the branch until archive-first retirement
evidence is complete.

### `feat/canonical-sos-contract`

Compared with current `main`: 13 unique commits.

Its principal SOS artifacts are already present in current `main`, including
the provider-neutral SOS domain contract, canonical SOS capability, contract
documentation, and tests. Current `main` also contains later convergence
evidence and canonical authorization/safety integration.

**Decision:** no wholesale merge. Preserve as historical source until the
archive-first retirement process permits retirement.

### `feat/capability-scoped-consent-agent-enforcement`

Compared with current `main`: 25 unique commits.

The branch contains an older parallel authorization model under
`src/authorization/`, older capability/consent policies, and agent policy
work. Current `main` has since converged on `src/access/`, the canonical
authorization policy, capability data scope, scoped execution, consequential
gate, consent capability, and the canonical agent gateway.

**Decision:** do not merge the parallel authorization implementation. Extract
only any missing evidence/tests/docs after semantic comparison. Preserve the
branch as historical source.

### `integration/canonical-platform`

Compared with current `main`: 12 unique commits.

Its Case/agent/platform documents and web composition work have already been
substantially superseded by the current canonical architecture.

**Decision:** no wholesale merge. Selective evidence only.

### `feat/canonical-case-kernel`

Compared with current `main`: 5 unique commits.

It proposes an alternative `src/domain/` + `src/application/` package split.
Current `main` has a different, already-integrated canonical layering under
`src/core/`, `src/capabilities/`, `src/access/`, `src/platform/`, and
`src/storage/`.

**Decision:** do not introduce a second domain/application authority merely
because the historical branch proposed it.

### `audit/postgres-provider-production-gates`

Compared with current `main`: 8 unique commits.

The branch contains useful audit material but also stale CI/pyproject and an
integration test written against an older Postgres adapter/migration boundary.

**Decision:** preserve useful audit evidence; do not merge stale implementation
or configuration wholesale.

## Responsibility-boundary rule reaffirmed

Code is split only when separation creates an independent boundary of:

- change/release cadence;
- trust/authorization;
- persistence/transaction ownership;
- provider/external-system dependency;
- deployment/runtime isolation;
- independent reuse.

Code remains cohesive when splitting would fragment invariants, state machines,
transaction semantics, or orchestration.

## Retirement rule

No sanctioned branch is deleted merely because its implementation is now
superseded. Before retirement:

1. unique work is identified;
2. useful work is extracted or explicitly rejected;
3. tests/evidence are preserved;
4. open PRs are absent;
5. archive reference exists;
6. retirement is executed through the controlled branch-retirement workflow.

## Current architectural conclusion

Current `main` is the canonical integration authority. Historical branches are
migration sources, not competing owners.

The nine-branch budget is therefore satisfied without forcing stale branch code
into the canonical architecture.
