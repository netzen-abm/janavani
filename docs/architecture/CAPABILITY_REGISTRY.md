# JanaVani Capability Registry

## Status

**Canonical registry — initial version.**

This registry identifies reusable capabilities that belong to shared JanaVani
infrastructure rather than to an individual surface.

## Rules

1. A reusable capability is defined once behind a provider-neutral contract.
2. Surface adapters may invoke capabilities but do not own their business logic.
3. Provider-specific SDKs remain inside provider adapters.
4. A capability must be independently testable without Telegram, WebApp,
   WhatsApp, or another surface.
5. Optional capabilities must remain optional at runtime.
6. No capability may silently perform an external action on behalf of a user.
7. New capabilities require a contract, ownership boundary, conformance tests,
   and an identified provider/adaptor boundary before becoming canonical.

## Registry

| Capability | Core responsibility | Surface-independent? | External action allowed? | Initial status |
|---|---|---:|---:|---|
| CASE | Case creation, lifecycle, persistence contract, evidence/document links | Yes | No | Implemented |
| AUTHORITY | Authority discovery, jurisdiction, authority relationships, escalation graph | Yes | No | Partial |
| DOCUMENT | Draft, review, correction, PDF/DOCX artifact generation | Yes | No | Contract implemented |
| RTI | RTI request/response workflow and assessment | Yes | No | Partial |
| FOLLOW_UP | Matter-aware next-action recommendation and reminders | Yes | No | Initial implementation |
| IDENTITY | Identity mode and citizen identity data handling | Yes | No | Partial |
| CONSENT | Explicit user consent records and policy decisions | Yes | No | Partial |
| EVIDENCE | Evidence references, provenance, integrity metadata | Yes | No | Partial |
| SEARCH | Search over authorities, offices, resources and case-support data | Yes | No | Partial |
| AI | Optional reasoning, drafting, extraction and assistance | Yes | No | Adapter layer |
| NOTIFICATION | User reminders and status notifications | Yes | No | Partial |
| AUDIT | Immutable/append-oriented operational and governance evidence | Yes | No | Partial |

## Capability boundaries

### CASE

Owns the canonical civic-case lifecycle and case-level relationships.

Does not own Telegram conversations, HTTP transport, database vendor APIs,
or document delivery.

### AUTHORITY

Owns authority identity, jurisdiction and procedural relationships.

It must become the source used by document generation for verified To/CC
metadata rather than allowing individual generators to read office CSV files
or hard-code addresses.

### DOCUMENT

Owns document drafts and artifact generation.

Outputs may include PDF and DOCX. A generated artifact is not a submission.
JanaVani does not send the artifact to an authority.

### RTI

Owns reusable RTI-specific case capabilities, including response review and
procedural next-action classification.

RTI may coexist with or precede/follow other civic actions.

### FOLLOW_UP

Owns adaptive next-action recommendations based on case history, matter
nature, documents, elapsed time, responses and user-reported outcomes.

The recommendation is not an automated external action.

### IDENTITY / CONSENT

These capabilities are cross-surface concerns and must not be implemented as
Telegram-only state or provider-specific records.

### EVIDENCE

Owns references and provenance/integrity metadata. Evidence must distinguish
user-reported information from externally verified information.

### SEARCH

Provides reusable search contracts. Search providers may vary without
changing consumers.

### AI

AI is an optional capability provider. Core deterministic workflows must not
require a particular AI vendor or model.

### NOTIFICATION

Notifications are user-facing reminders/status signals. They do not imply
submission, delivery, acknowledgement, or government response.

### AUDIT

Audit evidence records important capability operations and governance facts
without becoming a second source of truth for domain state.

## Adapter examples

```text
Telegram Webhook Adapter  -> CASE / DOCUMENT / FOLLOW_UP / NOTIFICATION
Telegram Mini App         -> CASE / DOCUMENT / FOLLOW_UP / SEARCH
WebApp                    -> CASE / DOCUMENT / AUTHORITY / RTI / FOLLOW_UP
Android                   -> shared capabilities
iOS                       -> shared capabilities
WhatsApp                  -> shared capabilities
Messenger                 -> shared capabilities
DApp                      -> shared capabilities
AI Agent                  -> approved capabilities only
```

## Provider examples

```text
CASE repository:
    memory -> PostgreSQL -> Supabase PostgreSQL adapter

AI:
    local model -> hosted model provider -> another provider

Storage:
    local -> PostgreSQL/object storage provider -> institutional deployment

Notifications:
    Telegram -> WhatsApp -> push/web notification
```

These are replaceable implementations, not architectural commitments.

## Conformance requirement

Every implementation of a capability contract must pass the same core
contract suite. Provider-specific tests may be added in addition to the core
suite.

## Anti-patterns

Do not create:

- TelegramCaseService when a shared Case capability is appropriate;
- WebAppDocumentService containing document business rules;
- Supabase-specific domain models;
- Langflow-specific case state;
- Cloud Run-specific lifecycle semantics;
- provider-specific identifiers as domain identifiers unless explicitly
  represented as external references;
- any `send_document()` capability.

## Evolution rule

Before adding a new function, ask:

> Could another JanaVani surface or future provider reasonably need this?

If yes, place it behind shared infrastructure. If no, keep it local to the
adapter and document why.
