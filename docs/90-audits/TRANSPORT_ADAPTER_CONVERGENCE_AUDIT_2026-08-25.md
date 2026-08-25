# Transport Adapter Convergence Audit — 2026-08-25

## Scope
This audit covers the current Telegram transport implementations as the first transport/channel convergence target. The same method will be applied to WhatsApp, Messenger, Web/API, DApp, and future adapters.

## Evidence
The repository contains multiple Telegram generations:
- `src/bot_telegram.py` — standalone polling bot entrypoint.
- `src/adapters/telegram_client.py` — client adapter for an isolated AI service.
- `janavani_v2/src/adapters/telegram_webhook.py` — legacy webhook generation.
- `janavani_v3/src/adapters/telegram_webhook.py` — later webhook generation.

The v2 webhook contains two consecutive implementations of the same `/incoming` route, duplicated imports and inconsistent model definitions. It also references `Optional` and `Field` without importing them. This is a clear multi-generational/staked-code defect.

The v3 webhook repeats the same architectural pattern and adds blocking `time.sleep()` inside an async endpoint. It is not treated as the canonical transport implementation.

## Disposition
Following **Archive first. Delete only after evidence**:
1. Preserve v2 under `docs/archive/legacy/janavani_v2/...`.
2. Preserve v3 under `docs/archive/legacy/janavani_v3/...`.
3. Do not delete source generations yet; deletion requires deployment/import evidence.
4. Do not copy either implementation into the new platform layer.
5. Treat `src/bot_telegram.py` as a standalone surface entrypoint, not the capability contract.
6. Treat `src/adapters/telegram_client.py` as an AI-service integration adapter, not the webhook transport.

## Target boundary
```text
Telegram Bot / Mini App
        |
        v
Telegram Transport Adapter
        |
        v
Channel-neutral CapabilityRequest
        |
        v
CapabilityRegistry / shared capabilities
        |
        +--> Document
        +--> Storage
        +--> AI
        +--> Civic workflows
```

The Telegram adapter translates Telegram-native events into Janavani capability requests and must not duplicate domain, workflow, document, AI, storage, or policy implementations.

## Independence
Telegram must remain independently operable. A Telegram outage must not disable Web, Android, iOS, DApp, WhatsApp, Messenger, CLI, or other surfaces.

## Privacy and safety
Transport adapters must not introduce tracking identifiers merely for convenience. Authentication, authorization, consent, privacy policy, rate limiting, replay protection, input validation, secret handling and safe errors belong to explicit policy/security boundaries rather than duplicated ad hoc in each channel generation.

## Next step
Before deletion, inspect deployment configuration, route registration, imports and runtime references for v2/v3. Then build the canonical Telegram transport contract and deterministic adapter tests.
