# Canonical Janavani WebApp

This directory is the product WebApp boundary. It is intentionally independent of legacy `janavani_v3` UI code.

## Rules

- UI consumes shared capability contracts; it does not own domain/business logic.
- Private Case/Evidence state is local-first and must use the LocalVault boundary.
- Remote APIs are used only for capabilities that require them.
- AI and Agentic AI receive non-personal allow-listed context only.
- No `localStorage` is permitted for Case content or key material.
- Provider-specific technology is accessed through adapters/capability routing.
- The WebApp must remain usable when optional providers are unavailable.

## Planned client modules

```text
src/webapp/
  README.md
  contracts.js
  capabilities.js
  privacy.js
  vault.js
  case-store.js
```

The first production vertical slice is:

`Create Case → Evidence → Authority → Document → Review → Submit → Track`

This is a client boundary specification until the canonical build toolchain is selected and verified.
