# Rust Generation Audit

**Date:** 2026-09-04  
**Status:** Baseline audit for canonical Rust/Web convergence

## Finding

Janavani already contains multiple historical Rust/Dioxus generations. The repository search confirms active `src/web_dioxus` and historical `janavani_v2` / `janavani_v3` application trees. These are not to be treated as competing canonical runtimes.

## Canonical decision

| Asset | Disposition | Reason |
|---|---|---|
| `crates/janavani-core` | **Canonical / active** | Shared domain kernel; language/runtime-neutral from surfaces and free of transport/storage/UI dependencies |
| `crates/janavani-application` | **Canonical / active** | Shared use-case boundary for Web, Telegram and future surfaces |
| `src/web_dioxus` | **Existing Web implementation / migration source** | Real Dioxus client already exists; audit and reuse incrementally rather than recreate |
| `janavani_v2` | **Historical / archive candidate** | Generation-specific application tree; do not extend as a new canonical root |
| `janavani_v3` | **Historical / archive candidate** | Generation-specific application tree; do not extend as a new canonical root |
| root Rust package | **Compatibility/scaffolding** | Existing decentralized capability scaffolding; not the canonical domain kernel |

## Important constraint

This audit does **not** delete or archive any generation yet. Archive eligibility must be established from dependency/reference/build evidence first. This preserves the archive-first rule.

## Target Rust layering

```text
Surface adapters
  Web/Dioxus | Telegram | WhatsApp | future mobile
          |
          v
janavani-application
  use cases / application contracts
          |
          v
janavani-core
  domain entities / invariants / lifecycle / events
          |
          v
provider adapters
  PostgreSQL | Supabase | memory | external systems
```

The application crate must not become a second domain model. It orchestrates use cases and ports; canonical invariants remain in `janavani-core`.

## Web implication

The existing Dioxus Web client is a migration asset, not a reason to replace the public static website. The intended hybrid model is:

- public/SEO website remains independently deployable;
- citizen workspace evolves as a Dioxus/WASM surface;
- both consume the same ecosystem/application contracts where appropriate;
- no UI surface owns CivicCase lifecycle rules.

## Next audit gates before archival

1. Identify imports/references from active code, scripts and CI into `janavani_v2`, `janavani_v3`, and `src/web_dioxus`.
2. Determine which historical capabilities have no equivalent in the canonical kernel/application boundary.
3. Preserve any unique capability as migration evidence before archiving.
4. Archive only after evidence and CI/build checks show the active path no longer depends on it.
