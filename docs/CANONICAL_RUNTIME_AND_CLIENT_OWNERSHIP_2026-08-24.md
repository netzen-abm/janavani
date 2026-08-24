# JANAVANI — CANONICAL RUNTIME & CLIENT OWNERSHIP

**Date:** 24 August 2026  
**Status:** P0/P1 evidence map  
**Scope:** Runtime entrypoints, App/DApp foundation, legacy generations and deployment ownership.

## Decision

The repository must converge on one canonical implementation per responsibility while retaining optional adapters and historical generations until dependency evidence permits archival.

**First construction focus:** Android + iOS App and DApp/Web3 client foundation.

**Product scope remains the full ecosystem:** Web/WebApp, Telegram Bot/Mini App, WhatsApp, Messenger, Nostr, Nym, Reticulum, Freenet, blockchain/ZKP, AI/Agentic AI/SLM/RAG/VLM/LAM/MoE/MLM/SAM/LLM/OCR/computer vision and future protocol adapters.

No optional protocol or provider is a mandatory runtime dependency for unrelated capabilities.

## Current evidence

### Python API

`src/web/canonical_app.py` is the explicit canonical FastAPI assembly. It imports four domain routers and exposes `/liveness` and `/version`. It intentionally avoids importing historical `src.web.app`. This is the current canonical API assembly boundary.

### Problem discovered

The root `Dockerfile` still launches `src.web.app:app`, not `src.web.canonical_app:app`. It also contains two concatenated Docker stages with different Python versions and different entrypoints. This is an ownership ambiguity and must be resolved before calling deployment canonical.

`Procfile` launches `src.bot_telegram`, which is a channel adapter rather than the canonical platform API. This is acceptable only if the deployment target is explicitly a Telegram-only process; it must not be treated as the general Janavani runtime authority.

### Rust/Dioxus client

`src/web_dioxus/Cargo.toml` defines a Dioxus web package. Search evidence also shows parallel Dioxus trees under `janavani_v2/` and generation-specific source files. Therefore `src/web_dioxus/` is the current root client candidate, but Android/iOS/DApp ownership is not yet established by a single canonical workspace.

The current `src/web_dioxus/src/main.rs` contains multiple concatenated `main.rs` implementations in one file. This is a high-priority cleanup target because it creates ambiguity over which UI implementation is authoritative and may not compile as a normal Rust source file.

## Ownership matrix

| Responsibility | Current candidate | Classification | Next action |
|---|---|---|---|
| Python API assembly | `src/web/canonical_app.py` | CANONICAL CANDIDATE | Keep; verify all deployment entrypoints point here |
| Legacy Python web app | `src/web/app.py` | LEGACY | Keep until import/deployment audit proves removable |
| Web MVP | `src/web_mvp/` | HISTORICAL CANDIDATE | Dependency map, then archive if unused |
| Root Dioxus web client | `src/web_dioxus/` | CANONICAL CLIENT CANDIDATE | Clean source tree and establish workspace contract |
| v2 implementation | `janavani_v2/` | HISTORICAL/PARALLEL | Reuse-by-evidence only; no blind deletion |
| v3 implementation | `janavani_v3/` | EXPERIMENTAL/PARALLEL | Reuse-by-evidence only; no blind deletion |
| Android | Not yet uniquely established | GAP | Create canonical Android module under client boundary |
| iOS | Not yet uniquely established | GAP | Create canonical iOS module under client boundary |
| DApp/Web3 | Capability exists in architecture, client ownership not yet unique | GAP | Establish independent DApp client boundary |
| Telegram | `src/bot_telegram.py` plus generation-specific adapters | DUPLICATE/ADAPTER | Define channel contract and select implementation |
| WhatsApp | `src/bot_whatsapp.py` plus generation-specific adapters | DUPLICATE/ADAPTER | Same |
| Messenger | `src/bot_messenger.py` | ADAPTER | Define channel contract |
| Production deployment | Multiple candidates | AMBIGUOUS | Establish one production authority |

## Independence contract

Each client/channel/transport/model adapter must satisfy:

1. It can be disabled without preventing unrelated capabilities from running.
2. Provider outage results in explicit degraded/unavailable state, not global failure.
3. User can opt into optional Web3/decentralized/AI transports independently.
4. Core civic drafting, information, evidence and document workflows must not require blockchain, Nostr, Nym, Reticulum, Freenet or a specific AI provider.
5. External submission is never reported as successful until acknowledgement is obtained.
6. Local/offline operation may draft, store and prepare; it must not fabricate remote delivery.
7. Adapter contracts must permit future Web4/Web5/Web6 or other protocols without changing core domain contracts.

## P0 actions

- [ ] Make deployment target `src.web.canonical_app:app` where the deployment is the general Janavani API.
- [ ] Split/replace the concatenated root Dockerfile into one authoritative production image definition.
- [ ] Establish explicit channel processes separately from the API runtime.
- [ ] Establish one canonical Rust/Dioxus workspace layout.
- [ ] Split the concatenated `src/web_dioxus/src/main.rs` into one authoritative source implementation plus separate modules/components.
- [ ] Define Android, iOS and DApp as first-class client modules without coupling them to one another.

## P1 actions

- [ ] Compare root client modules with `janavani_v2` and `janavani_v3` by capability, tests and imports.
- [ ] Migrate reusable code into canonical modules rather than copying generations wholesale.
- [ ] Mark superseded generation files for archive only after dependency evidence.
- [ ] Define shared capability contracts independent of transport/client implementation.
- [ ] Add failure-isolation tests across transport and provider adapters.

## Do not do yet

- Do not delete `janavani_v2/` or `janavani_v3/`.
- Do not delete `src/web/app.py` merely because canonical assembly exists.
- Do not make blockchain/Nostr/Nym/Freenet a core dependency.
- Do not make a single AI provider a core dependency.
- Do not merge Telegram/WhatsApp/Messenger into the core API runtime.
- Do not claim Android/iOS/DApp are complete until build/test evidence exists.

## Completion gate

This document is complete only when the repository has:

- one verified API runtime authority;
- one verified client workspace authority;
- independent Android/iOS/DApp boundaries;
- channel adapters behind explicit contracts;
- no accidental dependency from one optional capability to another;
- build/test evidence for each promoted client;
- an archive map for superseded generations.
