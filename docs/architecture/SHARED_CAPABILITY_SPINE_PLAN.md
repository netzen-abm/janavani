# Janavani — Shared Capability Spine Plan

**Status:** ACTIVE IMPLEMENTATION PLAN  
**Scope:** Full Janavani product/ecosystem

## Objective

Turn the existing Capability Gateway architecture contract into a concrete,
testable composition layer shared by WebApp, Telegram and future surfaces.

The first implementation target is the civic case capability because Case is
the durable lifecycle anchor for the broader civic-action ecosystem.

## Current implementation

`src/capabilities/civic_case.py` provides a surface-neutral creation contract
that composes:

```text
IdentityContext
      ↓
Authorization Kernel
      ↓
CivicCase Capability
      ↓
Canonical CivicCase domain
      ↓
CivicCaseRepository
```

It accepts no Telegram, HTTP, Dioxus or other surface framework types.

## Required convergence sequence

1. **Case capability** — create/get/edit/review/approve lifecycle behind one
   contract.
2. **Authority capability** — jurisdiction and office discovery behind one
   contract.
3. **Evidence capability** — reference/provenance/local-first lifecycle.
4. **Document capability** — composition/export behind one contract.
5. **Consent/approval capability** — explicit user authorization for
   consequential actions.
6. **Submission preparation capability** — prepare, validate and track a
   submission without claiming delivery prematurely.
7. **Follow-up capability** — next action, reminder and outcome recording.
8. **Typed surface clients** — WebApp and Telegram consume the same contracts.

## Non-goals

This milestone does not:

- select the final cloud provider;
- make Render/Vercel/Cloudflare/Google Cloud a domain dependency;
- implement external government submission prematurely;
- replace citizen authentication with a user-supplied actor ID;
- move sensitive evidence into development/free-tier infrastructure;
- rewrite the entire Python edge into Rust;
- create a second business-logic implementation for Telegram or WebApp.

## Completion gate

A capability is promoted only after implementation, contract tests, surface
integration, persistence verification, security/privacy review and runtime
verification are available as evidence.

The vertical slice is a verification sequence within the full ecosystem; it
is not an MVP boundary.
