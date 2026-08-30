# Janavani Shared Capability Layer

This package is the channel-neutral boundary for Janavani capabilities.

Access surfaces (WebApp, Telegram Bot, Telegram Mini App, and future channels) must call capabilities rather than directly accessing channel-specific storage or business services.

## Initial capability contracts

- `case.py` — canonical Case lifecycle
- `authority.py` — authority discovery
- `evidence.py` — evidence and provenance
- `document.py` — document composition/generation
- `tracking.py` — case tracking
- `feedback.py` — ratings and feedback

## Rules

1. Capabilities are channel-neutral.
2. Providers and storage implementations remain behind capability boundaries.
3. Personal data is subject to Janavani privacy/consent policy before remote processing.
4. AI/Agentic AI is an ecosystem capability; whether a citizen invokes it is a user choice.
5. Capability failure must be represented explicitly; channels must not silently substitute unrelated storage or services.
