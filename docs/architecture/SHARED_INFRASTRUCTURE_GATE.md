# Janavani Shared Infrastructure Gate

## Status

**MANDATORY architectural rule.** This gate applies to every new Janavani skill, capability, feature, function, workflow, provider integration, security control, data service, UI behavior with reusable business semantics, and infrastructure component.

## Rule

Before implementation, explicitly determine whether the proposed work can be a reusable shared capability or infrastructure component.

If it can, it MUST be implemented once at the shared layer and exposed to access surfaces through stable contracts.

If it genuinely cannot be shared, the implementation must document why, including the boundary that makes it channel- or provider-specific.

## Required review questions

1. What problem does this solve?
2. Is it a reusable capability, policy, service, provider adapter, or infrastructure primitive?
3. Can WebApp, Telegram Bot, Telegram Mini App, Mobile, DApp, or future channels consume it?
4. Can it be expressed through a stable channel-neutral contract?
5. What data does it require, and can that data be minimized?
6. Does it require user choice or consent?
7. Does it invoke AI or Agentic AI? If yes, does it pass the shared privacy/policy gates?
8. Does it create a consequential action? If yes, is explicit confirmation required?
9. Can the implementation work without a specific vendor/provider?
10. What provenance/audit information is required without copying private payloads?
11. What is the deterministic/manual fallback if the provider or AI is unavailable?
12. What tests prove the shared boundary and its privacy/safety invariants?

## Implementation sequence

```text
Idea
  -> Shared Infrastructure Gate
  -> Capability / Policy Contract
  -> Minimum Data Definition
  -> Privacy / Consent Policy
  -> Provider Adapter (if needed)
  -> Access-Surface Adapter
  -> Tests
  -> Documentation
```

## Access-surface rule

Telegram, Telegram Mini App, WebApp, Mobile and future interfaces are **consumers** of shared capabilities. They must not become the owners of reusable business logic merely because a feature is first delivered through one channel.

## AI rule

AI is a core Janavani shared capability. **AI usage is controlled by the user.** User choice to use AI does not grant unrestricted access to personal/sensitive data and does not grant permission for consequential actions.

## Privacy rule

Personal and sensitive information remains on the user's device by default. External processing requires capability-specific minimization, policy evaluation, and the appropriate explicit authorization. Unknown or unclassified data is fail-closed.

## Output rule

When a capability produces a document, it must use the shared document model. The user chooses the final output format, currently PDF or editable Document (.docx). Access surfaces must not implement separate document-generation logic.

## Completion criterion

A new capability is not considered architecturally complete until its shared-infrastructure assessment is recorded and its reusable boundary is tested.
