# Janavani WebApp — Implementation & Deployment Audit

## Audit date
2026-08-29

## Executive assessment

The WebApp is in **foundation/prototype integration**, not production-ready. The strongest completed area is the local-first security/storage boundary. The major remaining work is product integration, browser runtime verification, authority/document/action workflows, provider adapters, deployment hardening, accessibility, observability without personal-data leakage, and independent security review.

## Completed in the current canonical WebApp boundary

- Shared capability-oriented WebApp boundary separated from legacy UI.
- Versioned Case contract and repository boundary.
- Evidence capability and Case association.
- AES-GCM encrypted IndexedDB vault with typed namespaces.
- Authenticated record binding using namespace, record ID, and envelope version.
- Device Key Provider abstraction.
- Browser session/device key implementation and user-controlled recovery primitive.
- Recovery wraps the actual vault data key; raw data key/passphrase are not stored by the recovery record.
- Shared WebApp bootstrap injects one vault into Case and Evidence capabilities.
- Local Evidence attachment capability with size limit and SHA-256 content fingerprint.
- Local attachment privacy inspection for obvious sensitive filename indicators.
- Browser verification harnesses for vault and key lifecycle behavior.
- Explicit architectural rule that AI/Agentic AI receive only allow-listed non-personal context.
- Explicit architectural rule that remote storage is never an automatic fallback for private Case/Evidence data.
- Provider-neutral design intent for future decentralized/alternative providers.

## Not yet production-complete

### P0 — must finish before public deployment

1. **Canonical build/runtime** — select and verify the actual WebApp framework/build/test pipeline; remove ambiguity between prototype HTML modules and the production application.
2. **Key lifecycle** — complete secure first-run, unlock, recovery, rotation, logout/lock, multi-tab/session behavior, device migration, backup/recovery UX, and failure semantics.
3. **Browser security tests** — execute the existing harnesses in real browsers and add automated Playwright/browser CI where appropriate.
4. **Attachment security** — embedded EXIF/XMP/IPTC handling, large-file/memory strategy, MIME/content validation, filename privacy, encrypted binary persistence verification.
5. **Case UX** — draft/edit/resume, validation, status model, error recovery, offline behavior, accessible navigation.
6. **Authority capability** — provider-neutral authority discovery, source provenance, freshness, confidence, jurisdiction, escalation and fallback behavior.
7. **Document capability** — templates, evidence references, jurisdiction-specific fields, local generation, reviewable drafts, export, integrity/versioning.
8. **Review + explicit submission** — human review, consent, destination selection, final payload minimization, transport adapters, submission receipt, retry/idempotency, cancellation.
9. **Tracking** — privacy-preserving local status tracking and remote-status adapters where explicitly needed.
10. **AI/Agentic AI gateway** — device-side PII detection/redaction/minimization, allow-list policy enforcement, consent, tool authorization/user approval, audit trail without personal-data leakage.
11. **Provider adapters** — government/open-data sources and future Nostr/IPFS/Freenet/Nym/Reticulum/DID/VC/ZKP/blockchain integrations behind capability/provider interfaces. No personal data or private keys on public/decentralized ledgers.
12. **Threat model + independent security review** — XSS/CSRF, supply chain, extension/device compromise assumptions, key recovery, attachment parsing, dependency audit, privacy threat model, abuse cases.
13. **Production operations** — CI/CD, CSP, secure headers, dependency pinning/scanning, backups only for non-private infrastructure, rate limiting, error handling, release process, rollback.

### P1 — required for a strong public product

- Multi-language/i18n architecture and accessibility (WCAG-oriented).
- Responsive mobile UX and installable PWA behavior if selected.
- Citizen onboarding and recovery education.
- Case/evidence search and organization without leaking data.
- Government source freshness/provenance UI.
- Analytics/telemetry designed to collect no personal Case/Evidence content.
- Provider health checks and graceful degradation.
- Feature/capability discovery where the citizen can choose whether to use available capabilities now or later.
- Documentation for capability contracts and provider adapters.
- End-to-end tests for the full vertical slice.

### P2 — expansion after first production release

- Telegram/WhatsApp/Messenger client adapters consuming shared capabilities.
- Native mobile clients.
- Advanced agentic workflows with explicit authorization.
- Decentralized providers including Freenet/Nostr/IPFS/Nym/Reticulum and DID/VC/ZKP/blockchain where appropriate.
- Community-owned/distributed infrastructure and federation.
- Advanced civic intelligence and analytics.

## First deployable product definition

The first release should be considered complete when a citizen can reliably:

`Create Case → Add optional Evidence → Discover Authority → Generate Document → Review → Explicitly Submit → Receive Receipt → Track`

while private Case/Evidence data remains local by default and any AI/Agentic AI interaction receives only approved non-personal context.

## Time estimate

Assuming focused full-time engineering and no major unknowns:

- **Functional alpha:** 3–5 weeks.
- **Private beta / pilot:** 6–10 weeks.
- **Production-ready v1:** 10–16 weeks.
- **Broader ecosystem release:** 4–8 additional months after v1, because multi-channel and decentralized providers require independent integration/testing/security work.

These are engineering estimates, not guarantees. Security review findings, government-provider availability, browser/platform constraints, and requirements discovered during runtime testing can extend the schedule.

## Recommended execution order

1. Canonical build/test runtime + storage/key lifecycle verification.
2. Complete Case + Evidence production UX.
3. Authority capability and provider contracts.
4. Document generation + review.
5. Explicit submission + receipt + tracking.
6. AI/Agentic privacy gateway and bounded tools.
7. Production security/operations hardening + independent review.
8. Pilot deployment.
9. Ecosystem adapters and decentralized providers as plug-in implementations.

## Definition of done for optional infrastructure

A provider is considered "optional" only from the **citizen's choice** perspective. The platform must expose a stable capability interface so a provider can be enabled later without redesigning the citizen workflow. Provider absence must produce graceful degradation, never data loss or unsafe fallback.
