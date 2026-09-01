# JANAVANI — CANONICAL AGENT PLATFORM CONTRACT

**Status:** ARCHITECTURE CONTRACT — INTEGRATION FOUNDATION
**Scope:** Shared Agentic AI infrastructure for the full Janavani ecosystem

## 1. Purpose

Define a provider-neutral, capability-first Agent Platform that can catalogue, approve, execute, resume, govern and observe agents across departments and independent Janavani surfaces.

This document is an architectural contract. It does not claim that every component is implemented.

## 2. Canonical components

```text
Agent Registry
      |
      v
Agent Identity
      |
      v
Agent Gateway / Policy Enforcement
      |
      +---- Model Armor
      |
      v
Agent Runtime
      |
      +---- Memory Bank
      |
      v
Shared Janavani Capabilities
      |
      v
Agent Observability
```

No component may become an implicit dependency of ordinary non-agent civic workflows.

## 3. Agent Registry

The registry is the catalogue and lifecycle authority for enterprise-approved agents.

Each published agent version must declare at minimum:

- stable `agent_id` and immutable `version`;
- purpose and owner/publisher;
- risk and autonomy class;
- capabilities and allowed workflows;
- tools and tool scopes;
- input/output data classes;
- identity, permission and consent requirements;
- supported channels and transports;
- model/provider references;
- memory policy;
- data residency/processing constraints;
- retention policy;
- human-approval requirements;
- provenance and verification state;
- dependencies and failure/fallback behaviour.

Lifecycle:

`DRAFT -> SECURITY_REVIEW -> PRIVACY_REVIEW -> TESTED -> APPROVED -> PUBLISHED -> ACTIVE -> DEPRECATED -> REVOKED/ARCHIVED`

Registry presence never implies execution authority.

## 4. Cross-department discovery

Departments discover agents only through the registry. Discovery results expose approval state, version, capabilities, permissions, risk class and data-handling constraints before invocation.

An agent published by one department may be reused by another only when the consuming workflow satisfies its declared policy requirements.

## 5. Agent Identity

Separate identities are required for:

- human principal;
- agent instance/type;
- execution/run;
- tool/service principal.

Never substitute an agent identity for the citizen identity.

Never give an agent unrestricted database credentials when a scoped capability interface can be used.

## 6. Agent Gateway

The Agent Gateway is the mandatory policy boundary between an agent and protected Janavani capabilities.

For every consequential call it evaluates, as applicable:

- principal and agent identity;
- requested capability/tool;
- authorization;
- consent;
- data classification and minimisation;
- jurisdiction and data residency;
- risk/autonomy level;
- rate and abuse policy;
- current agent version and revocation state;
- human approval requirement.

Decisions may be:

`ALLOW | DENY | REDACT | MINIMIZE | REQUIRE_APPROVAL | DEGRADED`

Agents must not bypass the gateway to reach protected production systems.

## 7. Model Armor

Model Armor is a policy/security layer around model input, retrieved context, tool calls and model output.

It must address, as applicable:

- prompt injection;
- untrusted retrieved instructions;
- tool poisoning / tool-output manipulation;
- excessive tool scope;
- data exfiltration attempts;
- unsafe output or policy violations;
- PII/sensitive-data leakage;
- untrusted content masquerading as authority.

Retrieved content is data, not authority.

Consequential actions must be re-validated after model generation and before execution.

## 8. Agent Runtime

The runtime owns long-running asynchronous execution.

Required state concepts include:

`CREATED -> QUEUED -> RUNNING -> WAITING -> CHECKPOINTED -> RESUMABLE -> COMPLETED | FAILED | CANCELLED | EXPIRED`

The runtime must support:

- durable run identifiers;
- explicit checkpoints;
- retry with bounded policy;
- pause/resume;
- cancellation;
- timeout/expiry;
- failure recovery;
- idempotency for external actions;
- version pinning or controlled migration;
- re-authorization after long pauses.

Time passing must not silently preserve obsolete permissions or assumptions.

## 9. Memory Bank

Memory is purpose-bound, classified and scoped. It is not an unrestricted transcript or citizen-data lake.

Memory classes:

1. Execution state — run/checkpoint/retry metadata.
2. Task context — minimum information required to resume a specific task.
3. Provenance context — source/version/reference metadata needed for truthful continuation.
4. User-controlled memory — persistent personal preferences or context, kept under the user's control where practical.

Long-running tasks must revalidate authorization, consent, source freshness, tool policy, agent version and applicable data constraints before consequential continuation.

Personal or sensitive citizen content must not be replicated into agent memory by default.

## 10. Autonomy model

Recommended autonomy levels:

- **L0 Observe:** read approved information.
- **L1 Assist:** draft/recommend/summarize.
- **L2 Prepare:** prepare an action but do not execute it.
- **L3 Reversible Execute:** execute bounded reversible operations.
- **L4 Consequential Execute:** explicit human approval required for each consequential action.
- **L5 Restricted:** no autonomous execution; dedicated governance required.

Each agent version declares its maximum autonomy.

## 11. Shared capability rule

Agents orchestrate shared Janavani capabilities; agents do not re-implement them.

Example:

```text
RTI Agent
  +-> Government Source/RAG capability
  +-> Office Directory capability
  +-> Case capability
  +-> Document capability
  +-> Evidence capability
  +-> Submission capability
  +-> Tracking capability
```

The same capabilities must remain independently consumable by Web, Android, iOS, Telegram, WhatsApp, Messenger, DApp and future surfaces.

## 12. Production data boundary

Agents interact with production data only through approved capability interfaces and policy enforcement.

Preferred pattern:

`Agent -> Gateway -> Capability -> Data boundary`

Prohibited default pattern:

`Agent -> unrestricted database`

Production access must be minimum-privilege, purpose-bound, time-bounded where practical and auditable.

## 13. Data sovereignty

Each agent/workflow declares processing location and residency constraints. The gateway must prevent transfer to an incompatible provider or jurisdiction.

Supported modes may include:

- `DEVICE_ONLY`;
- `JANAVANI_CONTROLLED`;
- `APPROVED_PROVIDER`;
- `DECENTRALIZED`.

Cloud AI and remote memory are never implied merely because an agent exists.

## 14. Observability

Agent observability should use structured, correlation-friendly telemetry with OpenTelemetry-compatible concepts where implemented.

Record, as appropriate:

- agent/version;
- run/execution id;
- capability/tool id;
- policy decision;
- approval event;
- timestamps and latency;
- success/failure/degraded state;
- source/provenance references;
- policy/security events.

Do not log full citizen narratives, private evidence, secrets or other sensitive payloads into ordinary telemetry.

## 15. Feedback and adaptation

A user-facing agent workflow must provide an explicit feedback path without silently expanding data collection.

Feedback should be classifiable as:

- correction;
- preference;
- quality issue;
- safety concern;
- policy concern;
- unwanted behaviour;
- feature request.

Feedback affects future workflow/prompt/configuration versions through controlled review, not by silently mutating production policy from a single interaction.

## 16. Conversational guidance

Agents should ask only the questions necessary to proceed safely and should expose the current step/state, what is needed next, and what action will occur.

Where a required decision is consequential, the agent must clearly distinguish:

- recommendation;
- prepared action;
- approved action;
- executed action;
- acknowledged outcome.

## 17. Failure isolation

Agent failure must leave a deterministic or guided non-agent path where the underlying capability is required to remain available.

AI/model/provider failure must not become a failure of unrelated civic capability.

## 18. OpenClaw-derived patterns adopted selectively

The following patterns are useful architectural references and are adopted only where consistent with Janavani's contracts:

- gateway-owned sessions and server-side authorization checks;
- scoped claims rather than trust based on client assertions;
- explicit session/run state;
- bounded context injection and controlled compaction;
- deterministic ordering for model-visible registries/tool definitions where required;
- explicit session/workspace isolation;
- human/operator checks around privileged actions.

OpenClaw is an external reference implementation, not a Janavani dependency or codebase to import wholesale.

## 19. Janavani invariants

1. User choice controls optional capabilities; the ecosystem contains the capability regardless of whether a particular user enables it.
2. Privacy by Design and Privacy by Default apply to agent execution and memory.
3. No false success or false authority.
4. No implicit cross-capability personal-data replication.
5. No agent bypass of capability/policy boundaries.
6. No unrestricted production credentials for agents when scoped capability interfaces are available.
7. No automatic consequential external action without the required approval.
8. No agent dependency for ordinary civic workflows unless the capability itself is explicitly agentic.
9. Every agent version is verifiable, revocable and auditable.
10. New model/providers/protocols are replaceable adapters, not hard-coded platform identity.

## 20. Implementation status

| Component | Current repository status |
|---|---|
| Agent Registry | Existing capability registry; agent-specific schema extension required |
| Agent Identity | Planning/foundation exists; implementation not complete |
| Agent Gateway | Historical/runtime gateway pieces exist; canonical boundary not complete |
| Model Armor | No canonical implementation verified |
| Agent Runtime | POC/runtime pieces exist; canonical long-running runtime not complete |
| Memory Bank | No canonical implementation verified |
| Agent Observability | Metrics/telemetry pieces exist; sensitive-data audit required |

Completion requires implementation + tests + security verification + privacy verification + operational evidence.
