# Janavani — Canonical Web Client Boundary

**Status:** Architecture decision record / audit checkpoint
**Branch:** `feat/canonical-web-boundary-audit`

## Decision

`janavani_v3/src/web_dioxus` is treated as a **legacy prototype generation**, not the canonical WebApp foundation.

The canonical WebApp must be built around provider-neutral capabilities and explicit boundaries:

```text
Web UI
  ↓
Application / Case orchestration
  ↓
Capability interfaces
  ├── CaseRepository
  ├── LocalVault
  ├── EvidenceStore
  ├── AuthorityDirectory
  └── Transport
        ↓
Platform providers
```

## Findings from v3 audit

### 1. UI and infrastructure are tightly coupled

The current `main.rs` owns UI state, privacy auditing, capability detection, and transport-triggered grievance submission in one application component. This makes it unsuitable as the canonical application boundary.

### 2. Legacy transport is too opinionated

`auto_transport.rs` automatically selects Nym, Reticulum, or HTTPS and embeds a transport token. Transport selection must become an explicit infrastructure capability rather than being silently coupled to the grievance UI.

### 3. Legacy privacy audit is not a security oracle

`privacy_audit.rs` performs useful local heuristics, but checks such as URL patterns, local-storage entry count, and `navigator.webdriver` cannot establish that a device is uncompromised. These results must be presented as diagnostics, not proof of security.

### 4. Legacy legal generation needs a legal-content boundary

`legal_shield.rs` generates legal documents directly from strings and embeds legal assertions. The canonical architecture must separate document generation from legal knowledge, jurisdiction validation, evidence handling, and user review.

### 5. Legacy storage must not be reused

The previous `HardenedSovereignStorage` implementation uses XOR with a repeating passphrase and browser `localStorage`. This is not authenticated encryption and must remain deprecated. The new WebVault provider is the replacement direction.

## Canonical WebApp rules

1. No Case data in `localStorage`.
2. No encryption-by-obfuscation.
3. No silent network transmission from local storage primitives.
4. Transport selection must be behind a capability/provider boundary.
5. Legal documents require explicit user review before submission/export.
6. Privacy diagnostics must never claim compromise detection beyond what the browser can actually establish.
7. The WebApp must not inherit v3 UI/application coupling merely because code already exists.
8. Reuse data models and tested primitives only after they pass the canonical boundary review.

## Migration disposition

| v3 component | Disposition |
|---|---|
| `main.rs` | Legacy reference; do not extend |
| `auto_transport.rs` | Extract concepts only; redesign boundary |
| `capability.rs` | Reuse heuristics selectively |
| `privacy_audit.rs` | Reuse diagnostic ideas; downgrade claims |
| `legal_shield.rs` | Preserve as prototype reference; redesign as reviewed document capability |
| old `HardenedSovereignStorage` | Deprecated; do not reuse |
| new `src/platform/web_vault.js` | Canonical Web storage-provider direction |

## Next implementation gate

Before integrating the vault into the user-facing WebApp, define and test the canonical `CaseRepository` / `LocalVault` contract and create a minimal Web client that depends only on those contracts.
