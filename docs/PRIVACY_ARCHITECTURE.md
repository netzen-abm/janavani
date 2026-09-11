# Janavani — Privacy Architecture

**Status:** CANONICAL / ACTIVE
**Version:** 3.0
**Date:** 11 September 2026

## 1. Non-negotiable boundary

**Janavani does not build a personal-data repository by default.**

The default architecture is device-first, privacy-preserving and capability-independent. Personal data belongs to the citizen and remains on the citizen's device whenever technically possible.

If a selected capability genuinely requires data to leave the device, transfer must be necessary, visible, minimized, encrypted, directed to the selected destination and bounded by an explicit retention rule.

## 2. Privacy by design and default

Privacy is a system invariant, not an optional mode.

Citizens may opt into additional capabilities such as AI services, decentralized networks, Web3/DApp functions, messaging integrations, mesh transports or external submission. Capability opt-in does not constitute blanket consent to unrelated data collection.

> **Capability opt-in is not data-collection consent.**

Every capability must explain what data it needs, why it needs it, where it goes and the relevant retention boundary.

## 3. Data domains

### Citizen device — primary personal-data domain

Where practical, the device holds drafts, case material, generated documents, attachments, evidence, identity information, contact details, preferences, local cryptographic keys and offline state. Sensitive local persistence should use platform-appropriate secure storage.

### Janavani infrastructure — capability execution domain

Infrastructure should process only the minimum payload necessary to execute the selected capability. Operational telemetry must be minimized and must not become a shadow citizen-profile database.

### External destination — selected action domain

Government authorities, messaging providers, AI providers, decentralized relays and blockchain networks are separate trust boundaries. A selected destination receives only the payload necessary for the authorized action.

## 4. Personal-data rule

Janavani must not permanently store personal data on its own servers by default, including names, addresses, telephone numbers, email addresses, precise location histories, government identifiers, identity documents, biometric information, private keys, wallet seed material, private communications or personal attachments.

If a selected workflow requires such information, it should be assembled locally and transmitted only when the citizen authorizes that capability.

## 5. Identity modes

Identity is a capability input, not a universal prerequisite:

- **Anonymous** — no personal identity where the destination does not require it.
- **Name only** — only the chosen name is inserted into the selected document.
- **Full identity** — locally supplied minimum contact information when required by the selected action.
- **Authenticated/cryptographic identity** — governed by the shared Identity, Access & Trust contract.

## 6. Sensitive data minimization

Janavani must not request sensitive identifiers or attributes merely for personalization, analytics, ranking or convenience. Examples include Aadhaar, PAN, date of birth, religion, caste, political preference, biometric information and continuous location history.

A selected legal/administrative capability may require a specific item. The reason must be clear to the citizen.

## 7. Transmission and encryption

Before sensitive data leaves the device:

1. identify the selected capability;
2. identify the destination;
3. minimize the payload;
4. obtain required user authorization/approval;
5. use authenticated encrypted transport;
6. avoid payload logging;
7. avoid retaining the payload beyond the necessary processing window;
8. isolate failure from unrelated capabilities.

TLS is required for conventional network APIs. Additional application-level or end-to-end encryption should be used where the selected protocol and threat model require it.

Encryption never makes unnecessary collection acceptable.

## 8. Capability isolation

Web, Android, iOS, Telegram, Telegram Mini App, WhatsApp, Messenger, API, DApp/Web3, Nostr, Nym, Reticulum, Freenet, blockchain/ZKP, AI, agentic AI, RAG, VLM, OCR and future capabilities are independent boundaries.

An optional capability's outage, compromise, refusal or unavailability must not disable unrelated capabilities or require silent replication of citizen data into another system.

## 9. User-controlled capability selection

The citizen decides which optional capabilities are active. One capability must not silently activate another or inherit its data permissions.

For example, Web use does not imply Web3; AI use does not imply cloud processing; messaging does not imply blockchain identity; and Android use does not imply other channel activation.

## 10. Local-first workflow

```text
Citizen input
    ↓
Local processing / validation
    ↓
Local encrypted storage, if chosen
    ↓
Capability selection
    ↓
Authorization / consent / approval
    ↓
Minimized encrypted transfer
    ↓
Selected destination
    ↓
Outcome / provenance
```

Where a workflow can safely complete locally, it should not require an unnecessary server round trip.

## 11. Retention

> **If Janavani does not need to retain data to provide the selected capability, Janavani should not retain it.**

Temporary processing data should be deleted as soon as operationally possible. External legal or administrative retention belongs to the relevant external destination and must not be confused with Janavani's own retention.

## 12. Public accountability data

Janavani may publish or aggregate non-personal civic information such as complaint counts, district trends, department trends, public-service indicators, office/service ratings and public government claims/evidence, provided datasets are designed to reduce re-identification risk.

## 13. Privacy review gate

Every new capability must answer:

1. Does it require personal data?
2. Can it work without personal data?
3. Can processing happen locally?
4. What exact data leaves the device?
5. Who authorizes that transfer?
6. Is the payload encrypted?
7. Where is the destination?
8. How long is it retained?
9. Can the citizen delete the local copy?
10. Does failure affect unrelated capabilities?
11. What provenance is retained for consequential actions?

If these questions cannot be answered, the capability is not ready for integration.

## 14. Architectural principle

**Janavani exists to empower citizens, not to profile them. Privacy by design, privacy by default, data minimization by architecture, capability isolation and citizen control are system invariants.**

## Related canonical documents

- `docs/IDENTITY_ACCESS_TRUST.md`
- `docs/ARCHITECTURE_DATA_BOUNDARY.md`
- `docs/SOURCE_OF_TRUTH.md`
- `docs/JANAVANI_MASTER_ARCHITECTURE.md`
- `docs/ARCHITECTURE_PRINCIPLES.md`
