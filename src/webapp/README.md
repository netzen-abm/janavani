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
- Optional means optional for the citizen; capability support remains part of the platform design.

## Local browser verification

Serve the repository from a local HTTP origin. Do not open the verification page as `file://` because browser module and IndexedDB behavior depends on the execution context.

From the repository root in PowerShell:

```powershell
py -m http.server 8000
```

Open:

`http://localhost:8000/src/webapp/browser_vault_verification.html`

A successful run must end with:

`ALL BROWSER VAULT CHECKS PASSED`

The harness checks encrypted Case create/read/update/list/delete behavior, absence of a known plaintext secret from raw IndexedDB records, presence of an encrypted envelope, and AES-GCM tamper rejection.

This is a browser acceptance harness. It does not prove protection against XSS, malicious extensions, a compromised browser/device, or other client compromise.

## Security rule

Never add a remote fallback to the local Case/Evidence persistence path. AI and Agentic AI integrations must pass through the privacy boundary and must receive only explicitly allow-listed non-personal context.

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
