# Legacy Capability Extraction Matrix — 2026-08-26

**Status:** Audit / convergence planning

## Purpose

Identify useful capability and infrastructure present in `janavani_v2` and `janavani_v3` before archival. This prevents valuable work from being discarded while preventing duplicate generations from becoming parallel runtime authorities.

## Initial evidence

### Privacy / device auditing

`janavani_v2/src/web_dioxus/src/privacy_audit.rs` contains two overlapping privacy-audit implementations plus a native OS integrity helper. The first checks browser URL/protocol/local-storage conditions; the second expands this with WebDriver and native root-marker checks. The file also contains duplicated type/engine definitions. This is useful evidence but is **not production security proof**.

`janavani_v3/src/web_dioxus/src/privacy_audit.rs` contains the second-generation form of the same `SovereignDeviceAuditor` implementation. It overlaps materially with the v2 implementation.

**Decision:** CONVERGE CONCEPT, DO NOT COPY CODE. Create one canonical device-security capability with explicit evidence levels and platform adapters. Do not claim MITM detection, extension detection, jailbreak/root detection, or environment compromise from these heuristics without platform-specific verification.

## Extraction rules

For every legacy capability:

1. Identify the user/business capability.
2. Identify reusable domain concepts.
3. Identify reusable interfaces/contracts.
4. Separate real functionality from heuristic/marketing claims.
5. Compare v2 vs v3 behavior.
6. Identify canonical replacement location.
7. Port only verified/reusable behavior.
8. Add tests for the canonical implementation.
9. Update capability and architecture documentation in the same change set.
10. Archive the legacy source only after dependency and runtime gates pass.

## Candidate categories

| Category | v2/v3 evidence | Convergence direction |
|---|---|---|
| Device privacy audit | Duplicate implementations | Shared security-capability contract + platform adapters |
| Dioxus UI | Separate generations | Client adapter only; no domain authority |
| Cargo/Rust configuration | Separate workspace generations | Compare dependencies/features before consolidation |
| Deployment scripts | v2/v3 contain production/deployment material | Extract reusable deployment primitives; canonicalize one authority |
| Documentation | Separate developer/contributor guides | Migrate unique operational knowledge into canonical docs |
| Privacy/security concepts | Repeated across generations | Consolidate into architecture/security contracts |

## Non-copy rule

Do not copy an entire v2/v3 file into canonical code merely because it contains a desired feature. Extract the contract and verified behavior. Re-test against the canonical capability boundary.

## No-fake-security rule

Heuristics such as URL patterns, local-storage size, WebDriver presence, or existence of a known `su` path are indicators only. They must not be presented as definitive proof that a device is compromised or that traffic interception exists.

## Archival gate

A legacy file/subtree becomes an archive candidate only after:

- unique capability inventory is complete;
- canonical replacement is identified;
- active imports/deployment consumers are cleared;
- tests exist for retained behavior;
- documentation is migrated;
- security claims are evidence-calibrated;
- Git history/archive preserves recovery.

## Current conclusion

`janavani_v2` and `janavani_v3` remain **LEGACY GENERATIONS**. They are sources for capability extraction, not runtime authorities. No subtree is archived solely on naming or age.
