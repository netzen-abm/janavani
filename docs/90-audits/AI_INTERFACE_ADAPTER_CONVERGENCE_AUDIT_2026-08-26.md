# AI Interface Adapter Convergence Audit — 2026-08-26

**Branch:** `refactor/document-capability-convergence`  
**Rule:** Archive first. Delete only after evidence.

## Scope

This audit covers the legacy Web and Telegram AI gateway clients under `src/adapters/`.

## Evidence

- `src/adapters/web_client.py` directly called `/api/v1/agent/draft` and carried a hard-coded default interface token.
- `src/adapters/telegram_client.py` directly called `/api/v1/agent/draft` and `/retrieve/{tracking_id}` and carried a hard-coded default interface token.
- Repository searches found no active constructor/call-site references to either client on the convergence branch.
- The canonical platform contracts already provide channel-neutral capability and transport boundaries.
- The canonical Telegram transport adapter is separate from AI capability ownership and must not call the AI gateway directly.

## Decision

Both legacy AI interface clients were archived under:

- `docs/archive/legacy/src/adapters/web_client.py`
- `docs/archive/legacy/src/adapters/telegram_client.py`

The active source files were then removed because reference tracing found no active consumers and their responsibilities are superseded by the shared capability/transport boundaries.

## Security finding

The legacy clients contained default interface-token values in source code. Even if these values are placeholders, this pattern is unsafe and must not be reproduced. Future adapters must obtain credentials from the explicit secrets/configuration boundary and must never commit usable credentials or token defaults.

## Target architecture

```text
Web / Telegram / Android / iOS / DApp / WhatsApp / Messenger / future
                              |
                              v
                     Transport adapter
                              |
                              v
                   CapabilityRequest
                              |
                              v
                     CapabilityRegistry
                              |
                     +--------+--------+
                     |                 |
                 Document             AI
                 capability        capability
                     |                 |
                 providers         AI adapters
```

An interface may use an AI capability, but it must not own or require a provider-specific AI gateway implementation. Failure of one AI path must return an explicit degraded/unavailable state without taking unrelated capabilities or interfaces down.

## Follow-up

Apply the same audit method to WhatsApp, Messenger, DApp, Web/API and future channel adapters. Do not copy the legacy AI-gateway client pattern into new adapters.
