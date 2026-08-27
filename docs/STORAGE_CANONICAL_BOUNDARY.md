# Janavani — Canonical Storage Boundary

**Status:** Implemented on `strategy/civic-action-workspace-kernel`  
**Purpose:** Define the persistence boundary used while Janavani converges its legacy and ecosystem storage paths.

## Decision

The canonical civic work object is `Case`. Application/domain code should depend on the provider-neutral `CaseRepository` protocol rather than directly on JSONL, Supabase, PostgreSQL, Redis, or another provider.

```text
Domain / Application
        |
        v
   CaseRepository
        |
   +----+----+
   |         |
   v         v
 JSONL    Supabase
 adapter    adapter
```

## Migration rule

`ComplaintRepository` remains temporarily because existing data and callers use complaint terminology. It now implements the canonical case lookup semantics while preserving legacy `complaint_id` compatibility.

No existing JSONL records are rewritten or deleted by this change.

## Contract

`src/storage/repositories/protocol.py` defines:

- `save(record)`
- `get_by_id(case_id)`

The contract deliberately accepts a serialisable mapping at this stage. A future schema/serialization layer may make the mapping strongly typed once the canonical persistence model is verified across environments.

## Verification

`tests/test_case_repository_contract.py` verifies:

1. canonical `case_id` round-trip through JSONL;
2. evidence references survive persistence;
3. event history is retained in the persisted representation;
4. legacy `complaint_id` records remain readable.

## Not yet claimed

This boundary does **not** claim that Supabase/PostgreSQL is production-ready. The repository reconciliation explicitly requires runtime verification before making that migration decision.

It also does not authorise deletion of legacy storage, migration of existing data, or selection of a hosted database as the sole production store.

## Next step

After the root verification suite is executable, implement and test the canonical Case serializer/repository service against the approved runtime storage adapter. Then reconcile every domain object in the storage ownership map against one canonical owner.
