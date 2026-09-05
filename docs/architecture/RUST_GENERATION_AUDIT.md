# Rust and Dioxus Generation Audit

## Purpose

This audit records the architectural disposition of the legacy Rust/Dioxus generations before any consolidation or archival action.

## Canonical direction

`crates/janavani-core` is the canonical Rust domain kernel.

`crates/janavani-application` is the provider-neutral application boundary.

Legacy Dioxus generations are not canonical domain implementations and remain outside the active Cargo workspace unless deliberately migrated.

## Generation findings

### `src/web_dioxus`

Older standalone Dioxus web application named `janavani-dioxus-web`, version `1.0.0`, with direct browser/runtime dependencies.

Disposition: **legacy candidate; do not merge into canonical workspace yet**.

Reason: it is a presentation/runtime generation and does not consume the canonical `janavani-core` or `janavani-application` contracts.

### `janavani_v2`

Separate Dioxus package named `janavani_v2`, version `2.0.0`, targeting web and mobile. It contains experimental SOS, protocol-overlay, accountability, and related capabilities.

Disposition: **legacy experimental generation; preserve for evidence, do not make canonical**.

Reason: capability ideas may be reusable, but the implementation is coupled to an independent application state and module structure rather than the current canonical boundaries.

### `janavani_v3`

Separate Dioxus package named `janavani_v3`, version `3.0.0`, targeting web, mobile, and desktop. It contains experimental transport, privacy-audit, capability, and legal-shield modules.

Disposition: **legacy experimental generation; preserve for evidence, do not make canonical**.

Reason: it contains architectural and security-sensitive experiments that require independent validation. It must not be promoted merely because it is newer by version number.

## Consolidation rule

Do not create `janavani_v4` or another generation label.

Future Rust/Dioxus work must build against the canonical crates and capability contracts. Reusable ideas from legacy generations should be extracted as small, independently reviewed capabilities rather than copied wholesale.

## Archive rule

No legacy generation is deleted by this audit. Archive or remove only after an evidence review confirms that required behavior, documentation, tests, and historical context have been preserved elsewhere.

## Immediate recommendation

1. Keep all three generations outside the canonical Cargo workspace.
2. Inventory reusable capabilities from each generation before archival.
3. Prioritize migration by capability value and contract compatibility, not generation number.
4. Address Python/Rust field-type parity in a dedicated change before relying on Rust as the full canonical case representation.

## Important parity finding

The Python canonical `CivicCase` represents `jurisdiction` as `dict[str, Any]` and `claims` as `list[dict[str, Any]]`. The Rust kernel currently uses narrower `BTreeMap<String, String>` representations. This is a known parity boundary and should be handled separately from legacy-generation cleanup.
