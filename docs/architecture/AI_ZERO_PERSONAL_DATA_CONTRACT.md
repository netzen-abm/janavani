# Janavani AI / Agentic AI Zero-Personal-Data Contract

## Absolute rule

No personal data may be shared with an AI model, LLM, SLM, VLM, RAG provider, embedding service, model gateway, Agentic AI runtime, agent tool, prompt service, evaluation service, or AI telemetry system at any point.

This rule applies even when the data is encrypted. Encryption does not make personal data eligible for AI processing.

## Required flow

```text
User device
  -> local vault
  -> allow-listed data minimization
  -> non-personal/synthetic context
  -> privacy gateway
  -> AI/Agent provider
```

## Enforcement requirements

- AI inputs must be constructed from allow-listed non-personal fields, not by serializing a Case/User object.
- Provider adapters must reject payloads that are not explicitly classified as non-personal.
- PII detection is defense-in-depth only; it is never the primary guarantee.
- Unknown classification fails closed.
- Personal evidence, identity information, contact details, credentials, identifiers, private messages, precise personal locations, or other user-specific sensitive data must remain local.
- AI-generated output must not be treated as authoritative without source/provenance validation.
- Agentic AI may not use personal data as hidden tool context.
- Agentic AI must use scoped tools and explicit authorization for consequential actions.
- AI provider outages must not make critical deterministic civic workflows unusable.

## Implementation requirement

Every AI/agent provider adapter and every route that can invoke AI must be tested for negative cases: personal-data injection, nested personal data, unexpected fields, unknown classification, provider failure, and attempts to bypass the privacy gateway.
