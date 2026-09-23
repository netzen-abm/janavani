# Capability-Scoped Consent

## Status

Canonical ecosystem security contract.

## Purpose

Consent is scoped to the capability, purpose, exact data fields, provider and processing mode. A prior approval is not blanket permission for unrelated processing.

## Decision sequence

`request → classify → minimum-data check → capability policy → scoped consent → execute`

## Rules

1. Unknown fields are denied.
2. A capability may request only fields declared by its policy.
3. Public/non-sensitive data may proceed without consent when the capability policy permits it.
4. Personal, sensitive and high-risk data require an exact consent scope unless an explicitly defined lawful/local path applies.
5. Consequential actions require explicit authorization and the applicable approval gate.
6. Consent for one purpose/provider/mode cannot be reused for another.
7. Consent does not override data minimization.
8. Declining optional data must not disable unrelated capability behavior.

## Agentic AI

Agents must pass data requests through the same canonical access controls used by other surfaces. Tool permission alone is insufficient.

The canonical Agent Gateway composes authorization, scoped execution, capability data scope, consent and consequential-operation controls. It is not a second policy engine.

## Provenance

Security decisions should use minimized provenance/audit metadata. Raw personal data, prompts, tokens and private evidence must not be copied into ordinary provenance merely to explain a policy decision.

## Surface reuse

The same contract applies to WebApp, Telegram, mobile, WhatsApp, Messenger and future agent interfaces. Surface identity is not itself authority.
