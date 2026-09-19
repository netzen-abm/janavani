# PostgreSQL RLS Negative-Test Harness

This harness is a disposable-database-only verification plan. It must not be run against the Janavani shared/production database.

## Required isolation cases

For principals `alice`, `bob`, `delegate`, and `service-a`:

1. Alice can read her own Case.
2. Bob cannot read Alice's Case.
3. Bob cannot update Alice's Case.
4. Alice cannot insert a Case owned by Bob.
5. Active delegate can read the delegated Case.
6. Delegate without `case:update` cannot update the Case.
7. Revoked delegate loses access.
8. Expired delegate loses access.
9. Delegate scoped to another resource cannot access Alice's Case.
10. Anonymous/no principal sees no private Case.
11. Service policy rows are not directly readable by ordinary client roles.
12. Child rows (events, evidence refs, documents, submissions) cannot bypass parent Case authorization.
13. Consent rows are accessible only to the consent subject under the canonical policy.
14. Historical Case events cannot be deleted through the ordinary Case policy surface.

## Execution contract

The harness must establish a trusted transaction-local setting:

`SET LOCAL janavani.principal_id = '...'`

and execute every assertion inside an isolated transaction/role context.

The candidate policy must be installed only on a disposable PostgreSQL database. The test must prove both positive and negative access before any production RLS activation is considered.

## Current blocker

The connected Janavani database has zero rows in the inspected Case/security tables, but RLS is disabled on all eight canonical security tables. Therefore this repository harness is the correct next gate; the shared database remains unchanged.

## Production gate

Do not mark P0.6e/P0.6f complete until these assertions execute against a real PostgreSQL instance with RLS enabled and pass.
