# Janavani AI & Agentic AI Privacy Contract

## Non-negotiable invariant

No personal data may be transmitted to an AI model, AI provider, RAG provider,
agent runtime, agent tool, telemetry service, or external AI dependency at any
point in any workflow.

This is a platform invariant, not a user preference.

## Required architecture

User device -> local data boundary -> privacy gateway -> sanitized/public context -> AI/Agent provider

The privacy gateway is a hard security boundary. Provider adapters must never
receive raw Case identity, contact details, Aadhaar, PAN, phone, email, exact
personal address, private evidence, credentials, private messages, or other
personal data.

## Allowed AI/agent context

Only data that is explicitly classified as non-personal and safe for external
processing may cross the gateway, such as public government information,
public laws/policies, public office information, synthetic examples, and
non-identifying case facts where the privacy policy permits them.

## Fail closed

If the platform cannot establish that a payload is non-personal, the request
must be blocked. No best-effort redaction may be treated as a guarantee.

## User choice

AI and Agentic AI are platform capabilities and therefore remain available as
features. The user decides whether to invoke them. User choice never weakens
the privacy invariant.

## Agentic actions

Agents must use explicit permissions, tool allow-lists, confirmation gates for
consequential actions, and audit records. Agent availability must never grant
access to personal data.

## Future providers

Local models, cloud models, RAG systems, agent frameworks, Freenet/Nostr/P2P
services, and future providers must implement the same contract through an
adapter. Adding a provider must not require changing WebApp/domain privacy
logic.
