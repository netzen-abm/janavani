# JanaVani Ecosystem Capability Matrix

**Purpose:** durable scope register so ecosystem direction is not lost between implementation sessions.

| Domain | Capability | User-selectable | Independence requirement | Initial priority |
|---|---|---:|---|---:|
| Clients | Android | Yes | Must not depend on another client | P0 |
| Clients | iOS | Yes | Must not depend on Android | P0 |
| Clients | Dynamic WebApp | Yes | Must not depend on mobile/DApp | P0 |
| Clients | DApp/Web3 | Yes | Must not be required by civic core | P0 |
| Messaging | Telegram | Yes | Independent adapter | P1 |
| Messaging | Telegram Mini App | Yes | Shared capability contracts | P1 |
| Messaging | WhatsApp | Yes | Independent adapter | P1 |
| Messaging | Messenger | Yes | Independent adapter | P1 |
| Network | Nostr | Yes | Independent adapter | P1 |
| Network | Nym Mixnet | Yes | Independent adapter | P1 |
| Network | Reticulum Mesh | Yes | Independent adapter | P1 |
| Network | Freenet | Yes | Mandatory ecosystem capability; opt-in participation | P1 |
| Web3 | Blockchain | Yes | Optional verification/records | P1 |
| Web3 | ZKP | Yes | Independent privacy/proof capability | P1 |
| Intelligence | OCR | Yes | Independent provider boundary | P1 |
| Intelligence | Computer Vision | Yes | Independent provider boundary | P1 |
| Intelligence | SAM | Yes | Independent provider boundary | P2 |
| Intelligence | VLM | Yes | Independent provider boundary | P2 |
| Intelligence | SLM | Yes | Local/provider-independent boundary | P1 |
| Intelligence | LLM | Yes | Provider-independent boundary | P1 |
| Intelligence | MLM | Yes | Provider-independent boundary | P2 |
| Intelligence | MoE | Yes | Provider-independent boundary | P2 |
| Intelligence | LAM | Yes | Provider-independent boundary | P2 |
| Intelligence | RAG | Yes | Source/provenance controlled | P1 |
| Intelligence | Agentic AI | Yes | Scoped tools + approval gates | P1 |
| Civic | Complaints | Yes | Core civic capability | P0 |
| Civic | Grievances | Yes | Core civic capability | P0 |
| Civic | RTI | Yes | Core civic capability | P0 |
| Civic | Petitions/representations | Yes | Core civic capability | P0 |
| Civic | Policy opinions/objections | Yes | Independent civic workflow | P0 |
| Governance | Bills/Acts/ordinances tracking | Yes | Evidence/provenance required | P0 |
| Governance | Constitutional analysis | Yes | Analysis must not impersonate judicial determination | P0 |
| Governance | Government schemes/events | Yes | Source-backed information | P0 |
| Accountability | Service ratings/reviews | Yes | Reports separated from verified findings | P0 |
| Accountability | Officer/service recognition | Yes | Evidence and fairness controls | P1 |
| Accountability | Escalation | Yes | Department/admin/legislative routes independent | P0 |
| Accountability | Government claim verification | Yes | Evidence/provenance required | P0 |
| Finance | Contributions | Yes | Isolated accounting/audit subsystem | P1 |
| Documents | PDF/DOCX generation | Yes | Must work without AI where possible | P0 |
| Identity | Consent/permissions | Yes | Cross-channel linking requires consent | P0 |
| Privacy | Local-first/offline | Yes | Must preserve user state during outages | P0 |
| Safety | Emergency/resilience | Yes | Stronger integrity and delivery controls | P1 |
| Future | New protocols / Web generations | Yes | Adapter + contract model | P2 |

## Priority

- **P0:** App/DApp/WebApp foundation and core civic vertical slice.
- **P1:** Important ecosystem capability or integration to establish after core contracts.
- **P2:** Expansion capability that must remain architecturally possible without being a current blocker.

This matrix is intentionally a scope register, not a claim that every listed capability is already implemented.

## Completion rule

A row may move to production-ready only when implementation, functional tests, security/privacy review, failure-isolation evidence, documentation and operational readiness are recorded.
