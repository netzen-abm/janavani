# JANAVANI — AI OPERATIONS, SAFETY & PRIVACY

**Status:** ACTIVE OPERATIONS GUIDE
**Date:** 23 August 2026

This document describes how AI-related capabilities are verified inside the broader Janavani ecosystem. AI is optional, replaceable platform infrastructure; it is not Janavani's identity or universal runtime dependency.

## 1. Canonical references

Before changing AI code, consult:

1. `docs/JANAVANI_ECOSYSTEM_CHARTER.md`
2. `docs/SOURCE_OF_TRUTH.md`
3. `docs/JANAVANI_MASTER_ARCHITECTURE.md`
4. `docs/CAPABILITY_REGISTRY.md`
5. `docs/MASTER_TASK_CHECKLIST.md`
6. current CI/test evidence

## 2. AI safety principles

AI must:

- remain purpose-bound;
- preserve source/provenance distinctions;
- distinguish citizen-provided, authoritative, system-derived, expert-reviewed and AI-generated information;
- avoid fabricating authorities, legal provisions, evidence, government actions or delivery states;
- expose uncertainty where material;
- use deterministic or human-review paths for high-risk decisions where required;
- fail without breaking required non-AI platform capabilities.

## 3. Privacy principles

AI workflows must follow minimum necessary collection, privacy-preserving defaults, access control, retention discipline and secure handling of evidence and personal information.

Do not use logs, prompts or model traces as an uncontrolled secondary citizen-data store.

## 4. Verification

The repository's authoritative general test entry point is `run_all_tests.sh`, supplemented by the configured GitHub Actions workflows and capability-specific tests.

Do not reference test files that are not present in the current repository.

A passing unit test establishes only what that test verifies. It does not establish production readiness.

## 5. Runtime verification

AI runtime claims require evidence from:

- configuration;
- actual imports and call paths;
- provider/model configuration;
- execution results;
- failure/fallback behaviour;
- security/privacy tests;
- deployment/runtime evidence where applicable.

Documentation alone is not runtime evidence.

## 6. Provider independence

Provider-specific implementations must remain behind appropriate service/adapter boundaries where practical. Replacing an AI provider must not require rewriting Janavani domain logic.

## 7. Operational rule

When an AI capability is changed:

```text
Canonical docs
    ↓
Capability + dependency check
    ↓
Actual implementation inspection
    ↓
Targeted tests
    ↓
Full test/CI verification where required
    ↓
Security/privacy review
    ↓
Evidence update
    ↓
Checklist update
```

## 8. No overclaiming

The following states are distinct:

`VISION → DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → PRODUCTION-READY`

Never describe an AI feature as production-ready solely because its source file exists.
