# Janavani — Capability → Action → Resource → RLS Conformance Matrix

**Date:** 20 September 2026  
**Status:** SECURITY GATE — WORKING BASELINE  
**Purpose:** Reconcile implemented application authorization with the candidate PostgreSQL RLS boundary before production RLS activation.

## Source-of-truth rule

This matrix is derived from the active capability/access code and the candidate PostgreSQL policy. It does not create a second authorization vocabulary. Where the database cannot safely infer an application action from row data, the item remains **GAP / BLOCKER** until the boundary is explicitly designed and tested.

## Core invariants

1. Application authorization must fail closed.
2. PostgreSQL must independently prevent protected-row access outside the authorized principal boundary.
3. janavani.principal_id is transaction-local and must never be accepted from an untrusted client.
4. Delegation is bounded by delegate, grantor, capability, action, resource and expiry/revocation.
5. Consent is subject- and purpose/scope-bound.
6. Compound Case/Submission mutations must use one transaction and one principal context.
7. No ordinary client path may delete historical Case/security records.
8. Production RLS remains blocked until real-PostgreSQL negative tests pass.

## Implemented capability/action baseline

| Capability / component | Application actions observed | Primary resource | Database surface | Current RLS disposition |
|---|---|---|---|---|
| Civic Case | create, save, case:add_evidence, case:add_document, case:start_review, case:mark_ready, case:consent | Case | civic_cases + child refs/events | PARTIAL |
| Evidence | evidence:register, evidence:attach, evidence:read | Evidence / Case | civic_case_evidence_refs | PARTIAL |
| Consent | case:consent | Consent / Case | civic_case_consents | PARTIAL |
| Submission | case:begin_submission, case:submit, case:acknowledge | Submission / Case | civic_case_submissions + events | PARTIAL |
| Document Review | document:read, document:edit, edit | Document | Case document refs / document subsystem | GAP — mapping requires explicit review |
| Submission reconciliation | case:reconcile_submission at capability level; Case transition uses case:submit | Submission / Case | Submission + Case | GAP — requires explicit reconciliation policy |

## Case access matrix

| Principal state | Case SELECT | Case UPDATE | Case INSERT | Expected |
|---|---|---|---|---|
| owner | yes | yes | own principal only | ALLOW |
| stranger | no | no | cannot choose another owner | DENY |
| active delegate, resource-scoped | yes | only if delegated action permits | n/a | conditional |
| expired delegate | no | no | n/a | DENY |
| revoked delegate | no | no | n/a | DENY |
| no principal | no | no | no | DENY |

## Child-resource matrix

| Resource | SELECT | INSERT | UPDATE | DELETE | Required proof |
|---|---|---|---|---|---|
| Case events | inherit Case access | owner/delegated action | no ordinary policy | no ordinary policy | Must not permit a delegate to manufacture arbitrary history |
| Evidence refs | inherit Case access | evidence attachment capability/action | no ordinary policy | no ordinary policy | evidence:attach boundary |
| Document refs | inherit Case access | document/case capability boundary | no ordinary policy | no ordinary policy | Explicit document action mapping |
| Submissions | inherit Case access | submission capability + consequential gate | submission lifecycle only | no ordinary policy | case:submit + consent + approval |
| Consents | subject only | subject only | subject only | no ordinary policy | Subject identity, not Case visibility |
| Delegations | grantor/delegate visibility | grantor only | grantor only | no ordinary policy | Grantor control + expiry/revocation |
| Service policy | backend only | backend only | backend only | backend only | Ordinary client roles receive no access |

## Critical identified RLS gaps

### G1 — Child INSERT policies are currently broader than application action authorization

The candidate child INSERT policies primarily establish that the parent Case is visible. That is insufficient for delegated mutation.

A delegate who can read a Case must not automatically gain every child-write capability.

**Required resolution:** bind each child mutation to the smallest existing application capability/action that authorizes it, or make the database policy owner-only where the application action cannot be safely represented by row state.

### G2 — Delegation action vocabulary must converge

Application delegation evaluation checks the requested action directly. The candidate SQL currently contains action-specific checks such as case:update.

The conformance gate must verify exact action naming rather than assuming aliases.

**Required resolution:** establish a canonical action mapping from active code; do not silently normalize names in SQL.

### G3 — Audit table is not yet covered by the candidate RLS migration

public.civic_case_audit is a protected Case-derived record but is not currently part of the candidate RLS table set.

**Required resolution:** decide whether audit records are application-service-only and add an explicit database boundary. Ordinary clients must not be able to mutate or delete audit history.

### G4 — Document subsystem needs explicit cross-table authorization mapping

The active Document Review capability uses document:read, document:edit, and edit, while the Case document-reference RLS layer does not encode those actions.

**Required resolution:** reconcile document ownership/reference authorization before production RLS.

## Adversarial test matrix

Every row below must execute against disposable real PostgreSQL with a non-BYPASSRLS application-style role.

| Test | Principal | Operation | Expected |
|---|---|---|---|
| own-read | Alice | SELECT own Case | ALLOW |
| cross-read | Bob | SELECT Alice Case | DENY |
| owner-spoof | Alice | INSERT Case with created_by=Bob | DENY |
| own-update | Alice | UPDATE own Case | ALLOW |
| delegate-read | Bob | SELECT delegated Case | ALLOW |
| delegate-update-granted | Bob | UPDATE delegated Case with case:update | ALLOW |
| delegate-update-ungranted | Bob | UPDATE delegated Case without action | DENY |
| expired-delegate | Bob | SELECT after expiry | DENY |
| revoked-delegate | Bob | SELECT after revocation | DENY |
| wrong-resource | Bob | SELECT resource outside grant | DENY |
| consent-cross-user | Bob | SELECT Alice consent | DENY |
| child-bypass | Bob | SELECT Alice child row without Case access | DENY |
| child-write-bypass | Bob | INSERT child row without required capability/action | DENY |
| audit-mutation | Bob | UPDATE/DELETE audit record | DENY |
| service-policy | ordinary role | SELECT service policy | DENY |
| no-principal | no principal | SELECT protected data | DENY |
| context-leak | reused connection | second transaction without principal | DENY |
| rollback | authorized transaction | forced failure after mutation | no durable partial state |
| concurrency | two writers | same version | one deterministic conflict |
| idempotency | same key twice | repeated submission | one durable operation |
| restart | process/database restart | pending operation | state remains recoverable |
| backup-restore | restored database | protected data + policy | security behavior preserved |

## Production activation gate

RLS may not be activated until:

- all GAP items have an explicit design decision;
- candidate SQL and application action vocabulary agree;
- all adversarial tests pass against real PostgreSQL;
- application role is confirmed NO BYPASSRLS;
- migration/admin role is separate from application role;
- transaction-local principal isolation is proven;
- rollback/concurrency/idempotency tests pass;
- restart/recovery and backup/restore evidence exists.

**Current decision: DO NOT ACTIVATE PRODUCTION RLS.**
