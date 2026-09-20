# Admin Zero-Access Implementation Gate

**Status:** Enforcement roadmap
**Parent:** `docs/ADMIN_ZERO_ACCESS_SECURITY_CONTRACT.md`
**Tracking:** Issue #24 / PR #25

This document turns the architectural privacy contract into an implementation sequence. A policy statement is not considered sufficient evidence.

## Required enforcement layers

| Layer | Required property | Evidence |
|---|---|---|
| Data classification | Every capability explicitly classifies payload ownership/sensitivity | Automated classification tests |
| Client ownership | Sensitive/private data defaults to device-owned storage | Storage integration tests |
| Transport | Protected payloads require explicit user authorization and encryption | Transport tests |
| Capability isolation | Each capability has an independent data/key boundary | Isolation tests |
| Backend storage | No routine plaintext protected content is stored server-side | Schema/storage audit + tests |
| Logging | Sensitive values cannot enter logs, URLs, metrics or crash reports | Redaction tests |
| AI/ML | Providers receive only authorized/minimized inputs | Provider boundary tests |
| Administration | Admin/support APIs cannot retrieve protected content | Negative authorization tests |
| Key management | User decryption material is not exportable to ordinary admin paths | Key custody tests |
| Recovery | Recovery cannot create an administrator decryption backdoor | Recovery design/tests |
| Optional capabilities | Disabled capabilities receive zero user payload | Opt-in isolation tests |
| Production configuration | Debug/support bypass cannot weaken the boundary | Configuration gate |

## Current implementation

`src/core/privacy_boundary.py` provides the first dependency-free enforcement primitives:

- explicit data classes;
- independent capability identifiers;
- payload minimization;
- sensitive-field rejection;
- explicit authorization + encryption requirements.

`tests/test_privacy_boundary.py` proves these primitives in isolation.

## Next implementation order

1. Audit every persistent store and classify each field.
2. Audit every API/transport boundary for protected payload flow.
3. Add a common redaction layer before logs/telemetry/crash reporting.
4. Define capability-scoped storage and key namespaces.
5. Add negative tests for admin/support access to protected content.
6. Add AI/RAG/VLM/OCR/CV provider minimization tests.
7. Add configuration tests preventing debug/admin bypass.
8. Add deletion/export tests at the user-controlled data layer.
9. Run the full repository test suite and security checks.
10. Only then consider closing Issue #24 and merging the enforcement PR.

## Acceptance rule

The zero-access claim is **not complete** until CI demonstrates that an ordinary backend administrator has no routine plaintext access path to protected citizen content.

## Architectural constraint

New capabilities must implement this contract through an adapter/interface rather than modifying the privacy boundary itself. This keeps Android, iOS, Web, DApp, Nostr, Nym, Reticulum, Freenet, messaging, AI/ML and future protocol modules independently deployable and independently failure-tolerant.
