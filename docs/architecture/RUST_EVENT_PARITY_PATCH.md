# Rust CivicCase Event Parity Patch

## Scope

This patch is intentionally narrow.

It fixes three domain-contract defects:

1. Persist event `notes` on the stored event.
2. Keep `notes` separate from `source_ref`.
3. Validate event IDs before aggregate mutation.

## Maintainability rule

Rust code should prefer short, readable lines.

Target: keep ordinary lines at or below 88 characters where practical.

Long expressions should be broken across semantic boundaries.

## Non-goals

- No lifecycle changes.
- No persistence changes.
- No transport changes.
- No AI changes.
- No UI changes.
- No evidence-storage redesign.
- No new `IN_PROGRESS` operation.
- No new `ARCHIVED` operation.
