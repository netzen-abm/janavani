# Telegram Branch & Capability Audit — 2026-09-03

## Scope

Audit objective: identify Telegram code across branches and classify reusable
functions, features, capabilities, tools, resources, and surface-specific code.

## Branch inventory

The repository currently contains many branches. Telegram-relevant branches and
known historical generations include:

- `feat/telegram-shared-capability-migration`
- `feat/shared-civic-case-contract`
- `feat/shared-document-capability`
- `feat/converge-document-capability`
- `feat/shared-infrastructure-first-document-sources`
- `feat/webapp-civic-action-workspace`
- `feat/webapp-authority-evidence-vertical-slice`
- `feat/canonical-case-kernel`
- `feat/local-first-case-vault`
- `integration/canonical-platform`
- `develop/v0.2`
- `release/mvp-v0.1`
- `janavani_v2` code generation retained in repository history/tree
- `janavani_v3` code generation retained in repository history/tree

This list is an audit starting point, not an assertion that every branch above
contains Telegram implementation code. Each branch should be classified before
merge/archive decisions.

## Confirmed Telegram generations/files

### Current surface

- `src/bot_telegram.py`
- `src/adapters/telegram_client.py`
- `src/conversation/`

The active bot entry point uses `python-telegram-bot`, commands, callbacks,
message routing, and polling. Telegram is therefore clearly an adapter/runtime
surface, not merely documentation.

### Historical v2

- `janavani_v2/src/adapters/telegram_webhook.py`

The v2 implementation exposes a Telegram webhook adapter and forwards inbound
messages toward a core endpoint.

### Historical v3

- `janavani_v3/src/adapters/telegram_webhook.py`

The v3 implementation also exposes a Telegram webhook ingestion adapter and
uses a core URL boundary.

## Architectural classification

### Surface-only code — keep in adapter

Examples:

- Telegram `Update` / `ContextTypes` handling
- Telegram command handlers
- Telegram callback query handling
- Telegram keyboards/buttons
- Telegram webhook/polling lifecycle
- Telegram API client calls
- Telegram bot token loading
- Telegram-specific message rendering
- Telegram file upload/download operations

### Shared capability candidates — extract/retain outside Telegram

Examples:

- Civic Case creation/update/lifecycle
- issue classification
- matter/document sequencing
- authority/office resolution
- identity model
- consent semantics
- canonical document drafting
- PDF/DOCX generation
- evidence references/provenance
- RTI workflow
- RTI response assessment
- follow-up strategy
- reminders
- escalation recommendations
- outcome recording
- persistence/provider selection
- audit/accountability events

### Legacy code requiring controlled migration

- direct JSONL complaint persistence
- legacy complaint builder/generator paths
- direct office CSV lookup inside document generation
- old Flask runtime surfaces that start Telegram as a child process
- duplicate v2/v3 Telegram adapters

## Key findings

1. Telegram code exists in multiple generations.
2. The current bot entry point is Telegram-specific by design, which is correct
   for a surface adapter.
3. Several conversation steps import Telegram framework types directly. Those
   modules must not contain reusable domain/business decisions that other
   surfaces need.
4. v2 and v3 webhook adapters are potential sources of reusable transport/core
   separation patterns, but should not be merged wholesale.
5. The repository already states that the domain must remain independent of
   Telegram.
6. The canonical runtime entrypoint must not start Telegram/WhatsApp/Messenger
   as child processes.

## Function-level evaluation rule

For every Telegram-associated function, classify it as:

`ADAPTER` — only transport/UI mechanics.

`CAPABILITY` — reusable business/domain behavior; move behind a neutral contract.

`ORCHESTRATION` — workflow composition; move to a shared application/use-case
layer if more than one surface needs it.

`LEGACY` — preserve for compatibility, then archive after replacement evidence.

`DUPLICATE` — do not merge merely because it exists; select the authoritative
implementation.

`UNSAFE COUPLING` — Telegram, provider, or external service is embedded in
business logic and must be refactored.

## Capability-first acceptance test

A new function is not considered correctly placed if another JanaVani surface
would have to copy it to gain the same capability.

Preferred direction:

```text
Surface Adapter
      ↓
Shared Use Case / Capability
      ↓
Domain Contract
      ↓
Provider Adapter
```

Not:

```text
Telegram
   ↓
Business Logic
   ↓
Database
```

## Document delivery invariant

No Telegram implementation may send generated documents to authorities,
offices, email addresses, postal addresses, portals, or other external
destinations. Telegram may deliver the generated PDF/DOCX artifact to the user
for download. The user controls all subsequent delivery actions.

Follow-up reminders are allowed but do not prove submission, delivery, receipt,
or acknowledgement.

## Recommended convergence order

1. Extract shared capabilities from the active Telegram conversation flow.
2. Compare v2/v3 webhook implementations for useful transport patterns.
3. Keep one canonical Telegram adapter.
4. Retain compatibility facades only where consumers still exist.
5. Archive duplicate/obsolete Telegram generations after evidence.
6. Verify WebApp and Telegram consume the same contracts before expanding to
   Android/iOS/WhatsApp/Messenger/DApp.

## Branch policy

No branch should be merged merely because it contains more features.

Evidence required before convergence:

- capability value identified;
- ownership identified;
- dependencies identified;
- tests identified;
- compatibility risk assessed;
- canonical destination selected;
- duplicate implementations compared;
- archive path defined.

The repository's archive-first rule remains in force: archive before any deletion.
