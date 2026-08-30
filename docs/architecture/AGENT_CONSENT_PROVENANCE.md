# Agent Consent and Provenance Boundary

## Purpose

Agentic AI is a shared Janavani capability. The agent does not receive implicit permission to access data or perform actions merely because a tool exists.

Every agent tool request is evaluated against:

1. the capability policy;
2. the minimum data scope;
3. capability-scoped user consent when required;
4. tool risk;
5. explicit user confirmation for consequential actions.

## Canonical sequence

```text
Agent request
    -> capability policy
    -> consent scope
    -> tool data scope
    -> risk evaluation
    -> confirmation when consequential
    -> execute
    -> minimized provenance/audit
```

## Non-negotiable rules

- Consent is capability- and purpose-specific.
- Consent for one provider or processing mode cannot authorize another.
- A consent grant cannot widen the capability's minimum-data requirement.
- A tool cannot request fields outside the granted scope.
- Consequential tools require explicit user confirmation at the point of action.
- AI permission is not submission permission.
- Data consent is not action consent.
- Failed policy evaluation is fail-closed.

## Provenance

A successful or blocked agent operation should eventually emit minimized provenance containing identifiers and policy outcomes, not private case contents. The provenance record must never become a covert copy of the Case or Evidence payload.

Recommended event fields:

- event_id
- case_id/reference where applicable
- capability_id
- tool_id
- decision
- risk
- consent_scope_id/reference
- provider/model identifier where applicable
- timestamp
- confirmation_required
- confirmation_obtained

Private prompts, raw evidence and personal fields remain outside the provenance record unless a separate, explicit policy permits a specific field for an operational purpose.

## Failure behavior

If consent, scope, provider policy, or confirmation cannot be established, the agent must not execute the operation. The user should be offered a safe deterministic/manual path where the underlying capability supports one.
