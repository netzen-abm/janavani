# Storage Convergence Audit — 2026-08-25

**Status:** Active convergence audit  
**Branch:** `refactor/document-capability-convergence`  
**Rule:** Evaluate → Audit → Compare → Modify/Merge → Archive → Delete only with evidence

## Scope

Converge provider-specific storage implementations behind the shared Janavani storage capability without creating a new provider dependency or breaking independent interfaces.

## Evidence

The shared boundary is `src/platform/storage.py`. It defines `StorageAdapter` with `get`, `put`, and `delete`, returning the provider-neutral `StorageResult`. This is the intended dependency boundary for application/domain consumers.

`src/storage/supabase_adapter.py` implements that boundary for the current Supabase provider. Provider SDK access remains inside the adapter.

The former `src/storage/supabase.py` was a global singleton that imported `Config` through the legacy `core.config` path and constructed a provider client at module import time. Repository search found no active source imports of that singleton. The file has therefore been archived before removal.

`src/storage/supabase_client.py` is currently an empty placeholder and has no identified active references. It remains untouched pending a separate evidence pass.

`src/test_supabase.py` is a live diagnostic script that requires credentials and performs a real database query. The equivalent diagnostic is already preserved under `docs/archive/legacy/src/test_supabase.py`; it is not a deterministic unit test.

## Disposition

| Artifact | Status | Decision |
|---|---|---|
| `src/platform/storage.py` | CANONICAL CONTRACT | Keep |
| `src/storage/supabase_adapter.py` | CANONICAL PROVIDER ADAPTER | Keep; expand only through contract/tests |
| `src/storage/supabase.py` | LEGACY SINGLETON | Archived first, then removed after reference search |
| `src/storage/supabase_client.py` | EMPTY / ORPHAN CANDIDATE | Do not delete yet; separate audit required |
| `src/test_supabase.py` | LIVE DIAGNOSTIC | Preserve only if explicitly required; keep outside deterministic test suite |
| `docs/archive/legacy/src/test_supabase.py` | HISTORICAL DIAGNOSTIC | Preserve |

## Safety/privacy

Storage is infrastructure, not authorization. Capability policy, identity, consent, privacy and safety controls must be enforced before persistence. A storage provider outage must return a controlled failure/degraded state and must not make unrelated capabilities fail silently.

Provider replacement must not require clients to change their domain logic.

## Verification requirements

Before future storage changes are considered complete:

1. unit-test the storage contract using a fake provider;
2. test provider failure behavior without live credentials;
3. verify no interface imports provider SDKs directly;
4. verify no storage provider is required for unrelated deterministic capabilities;
5. verify privacy/authorization checks occur above the adapter boundary;
6. document any new provider or storage mode in the shared platform documentation;
7. preserve old implementations in archive until compatibility evidence is complete.

## Next steps

- audit repository classes under `src/storage/repositories/` once they contain active implementations;
- identify whether `analytics.py` and `cache.py` should use separate capability contracts rather than the general storage contract;
- evaluate the empty `supabase_client.py` with repository-wide references;
- add integration tests only as explicitly isolated, credentialed tests;
- keep local/offline/decentralized storage as replaceable future adapters rather than hard dependencies.
