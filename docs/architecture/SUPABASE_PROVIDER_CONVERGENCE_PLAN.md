# Janavani Supabase Provider Convergence Plan

**Status:** NEXT IMPLEMENTATION PLAN

## Sequence
1. Canonicalize identity-to-case authorization.
2. Reconcile live schema names/types with the canonical persistence contract.
3. Define a provider-neutral atomic mutation interface.
4. Implement the Supabase transactional RPC against the live schema.
5. Implement shared repository conformance tests.
6. Verify rollback, retry/idempotency and optimistic concurrency.
7. Enable RLS only after policy tests pass.
8. Keep the provider behind explicit runtime configuration.
9. Maintain the direct PostgreSQL provider as the portability reference.
10. Activate durable persistence only after all gates pass.

## Supabase role
Supabase is a replaceable PostgreSQL provider for the current MVP. The application must not assume Supabase-specific services.

## Transaction boundary
The atomic mutation covers, as applicable:
- civic case;
- lifecycle events;
- evidence/document references;
- required audit record;
- coupled submission + case lifecycle mutation where required.

The transaction must either commit the complete logical mutation or roll it back.

## RPC principle
Use one verified PostgreSQL function/RPC for each logical multi-table mutation. It must validate expected version, enforce idempotency, reject stale writes, preserve historical events, prevent duplicate references, return committed version/outcome, never manufacture external acknowledgement, and operate within the approved authorization boundary.

## Testing
Conformance tests must exercise the same behavioral contract against the direct PostgreSQL provider and Supabase provider:
- create;
- read;
- update;
- stale update;
- duplicate event;
- conflicting idempotency key;
- child-write failure/rollback;
- reference deduplication;
- concurrent mutation;
- restart/recovery;
- authorization denial;
- delegation expiry/revocation.

## RLS
RLS implementation is downstream of the authorization matrix. Never write RLS predicates from adapter fields merely because those fields happen to exist.

## Free-tier constraint
Avoid unnecessary Supabase services and remain within the free-service operating boundary. No paid-only architecture is required.
