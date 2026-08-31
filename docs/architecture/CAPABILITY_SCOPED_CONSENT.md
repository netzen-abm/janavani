# Capability-Scoped Consent

## Purpose

Consent is scoped to the capability, purpose, exact data fields, provider and processing mode. A prior approval is not blanket permission for unrelated processing.

## Decision sequence

`request -> classify -> minimum-data check -> capability policy -> scoped consent -> execute`

## Rules

1. Unknown fields are denied.
2. A capability may request only fields declared by its policy.
3. Public/non-sensitive data may proceed without consent when the capability policy permits it.
4. Personal, sensitive and high-risk data require an exact consent scope unless the capability policy explicitly establishes another lawful/local path.
5. Consequential actions require explicit authorization.
6. Consent for one purpose/provider/mode cannot be reused for another.
7. Consent does not override data minimization.
8. Declining optional data must not disable unrelated capability behavior.

## Agentic AI

Agents must pass every data request through the same evaluator. Tool permission alone is insufficient. Consequential tools require an explicit consent scope and user confirmation where required.

## Provenance

The policy decision, capability, approved data scope, provider/mode and resulting action should be represented by minimized provenance/audit metadata. Raw personal data must not be copied into the provenance record merely to explain a decision.
