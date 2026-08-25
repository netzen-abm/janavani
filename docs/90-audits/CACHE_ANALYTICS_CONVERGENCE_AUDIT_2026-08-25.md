# Cache and Analytics Convergence Audit — 2026-08-25

**Status:** Active convergence audit
**Branch:** `refactor/document-capability-convergence`
**Rule:** Evaluate → Audit → Compare → Modify/Merge → Archive → Delete only with evidence

## Findings

### Transient cache

`src/storage/cache.py` was not clean executable code. It referenced `os.getenv()` without importing `os` and imported `ai_settings` without using it. It also mixed provider construction and transient-cache semantics in one module.

The implementation has been repaired without changing its intended 30-minute bounded TTL behavior. It is explicitly marked as a legacy migration implementation while consumers are traced.

A new provider-neutral `src/platform/cache.py` contract now separates transient-cache semantics from Redis.

### Analytics

`src/storage/analytics.py` is a Redis-backed aggregate telemetry implementation. It does not belong behind the durable `StorageAdapter` merely because Redis is a storage technology. Analytics has distinct semantics and therefore receives its own `AnalyticsAdapter` contract under `src/platform/analytics.py`.

The current analytics implementation is intentionally aggregate-only and should not be extended to collect identity, IP addresses, raw citizen content, or unnecessary behavioral profiles.

## Architecture

```text
Capability / service
        |
        +-------------------+
        |                   |
   Cache contract      Analytics contract
        |                   |
   Redis adapter       Redis analytics
        |                   |
   transient TTL       aggregate metrics
```

Neither capability is a generic durable-storage substitute.

## Safety and privacy

Cache data is transient by design and must have explicit TTL semantics. Analytics must remain aggregate and privacy-preserving by default. Provider failure must not break unrelated civic capabilities.

## Next steps

1. Trace all consumers of `TransientStorageEngine` and `PrivacyPreservingAnalytics`.
2. Add fake-provider contract tests.
3. Build Redis adapters behind the new contracts only after consumer evidence is mapped.
4. Keep the repaired legacy implementation until migration is verified.
5. Archive before any later deletion.
