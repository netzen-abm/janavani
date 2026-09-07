# Janavani — Canonical Civic Action Spine

**Status:** ACTIVE IMPLEMENTATION CONTRACT  
**Scope:** Full Janavani ecosystem

## Purpose

Provide one reusable composition boundary for the civic-action path:

```text
Case
  ↓
Evidence references + provenance validation
  ↓
Verified Authority destination
  ↓
Document Draft
  ↓
Review / correction
  ↓
User-approved consequential action
```

The chain is a capability composition, not a surface workflow. WebApp,
Telegram, Mini App, mobile applications and future surfaces must consume the
same capability contracts.

## Invariants

1. A surface never owns CivicCase lifecycle business logic.
2. Evidence binaries remain under the applicable local-first/privacy policy;
   the capability handles references and validation, not silent transmission.
3. An authority destination is usable only when it resolves through the
   authority contract; Janavani must fail closed rather than guess.
4. Generated documents are artifacts for review, correction, printing or
   download. Generation does not imply submission or email.
5. External submission is a separate consequential capability and requires
   explicit authorization/approval.
6. Providers are adapters. PostgreSQL, Supabase, local stores and other
   providers cannot become domain dependencies.
7. Durable providers are required for continuity across independently deployed
   surfaces; process-local memory is for development/tests only.

## Current implementation state

- Canonical CivicCase capability: implemented.
- Provider-neutral CivicCase repository: implemented.
- PostgreSQL Unit-of-Work and CivicCase persistence: implemented.
- Canonical Evidence metadata/provenance contract: implemented.
- Canonical Authority record/repository contract: implemented.
- Canonical DocumentDraft/artifact contracts: implemented.
- Shared CivicAction composition capability: this branch.
- WebApp + Telegram migration to this composition boundary: next integration step.

## Promotion gate

Do not promote the capability to `main` until contract tests, both access-surface
integrations, persistence verification, security/privacy review and runtime CI
provide evidence.
