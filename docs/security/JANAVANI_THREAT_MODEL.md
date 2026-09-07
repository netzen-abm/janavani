# Janavani Threat Model

**Status:** Canonical threat-model baseline  
**Purpose:** Define the security boundaries, assets, actors, attack classes and required controls for the Janavani ecosystem.

## 1. System Boundary

Janavani is an ecosystem of independent access surfaces consuming shared capabilities and canonical domain infrastructure.

```text
Citizen / Operator
       │
       ▼
Access Surfaces
(Web / WebApp / Telegram / WhatsApp / Messenger / Mobile / future surfaces)
       │
       ▼
Capability + Policy Boundary
       │
       ├── Identity / Consent / Authorization
       ├── Case / Lifecycle
       ├── Evidence / Provenance
       ├── Document
       ├── Authority / Submission
       ├── AI / RAG / Agent capabilities
       └── Audit / Events
       │
       ▼
Storage / External Providers / Government-facing endpoints
```

No access surface should be treated as the security boundary by itself. A UI restriction is not authorization.

## 2. Security Objectives

Janavani must preserve:

1. **Confidentiality** — unauthorized parties cannot obtain protected citizen, case or evidence data.
2. **Integrity** — cases, evidence, documents, provenance, consent and lifecycle state cannot be silently or improperly altered.
3. **Availability** — failure or compromise of one access surface must not unnecessarily disable independent surfaces or shared capabilities.
4. **Purpose limitation** — data is used only for the authorized capability/purpose.
5. **User agency** — consequential actions require the user's explicit authorization at the appropriate point.
6. **Provenance** — originals and their transformations remain distinguishable and inspectable.
7. **Truth separation** — generated claims are not automatically treated as verified facts.
8. **Auditability** — consequential security-relevant actions leave appropriate evidence without creating unnecessary sensitive logs.

## 3. Assets

### High-value assets

- Citizen identity and contact information
- Authentication/session material
- Case records and lifecycle state
- Evidence originals and hashes
- GPS/location and timestamps
- Documents and generated drafts
- OCR and derived artifacts
- Consent and authorization records
- Authority/office information
- Submission and acknowledgement records
- AI/RAG context and retrieved sources
- Agent tool permissions and execution state
- Provider credentials and service secrets
- Audit/provenance records
- Build and release credentials/artifacts

### Integrity-critical assets

Evidence originals, original hashes, provenance, consent, authorization, approval/review state, lifecycle transitions and submission state require stronger integrity guarantees than ordinary presentation data.

## 4. Trust Boundaries

### Boundary A — Device ↔ Janavani

Threats include compromised clients, malicious extensions, modified applications, intercepted traffic, malicious uploads and unauthorized device access.

Controls: encryption, authenticated sessions where used, minimum disclosure, input validation, server/domain authorization, safe file handling and explicit consent.

### Boundary B — Surface ↔ Shared Capability

Threats include forged capability requests, unauthorized parameters, role/state manipulation and cross-surface inconsistencies.

Controls: canonical capability contracts, server/domain authorization, schema validation, policy enforcement and consistent lifecycle rules.

### Boundary C — Janavani ↔ External Provider

Threats include provider over-collection, provider substitution, credential compromise, malicious/compromised providers and unintended data disclosure.

Controls: provider policy, data minimization, scoped consent, encrypted transport, secret isolation, provider allowlisting where appropriate and auditable provider selection.

### Boundary D — AI/Agent ↔ Tools/Data

Threats include prompt injection, indirect injection, tool abuse, data exfiltration, context leakage and autonomous escalation.

Controls: tool-level authorization, least privilege, context isolation, data classification, output verification, explicit user confirmation for consequential actions and hard limits on agent autonomy.

### Boundary E — Build/CI ↔ Production

Threats include compromised dependencies, malicious Actions, leaked secrets, poisoned artifacts and configuration drift.

Controls: lockfiles, dependency scanning, workflow hardening, secret scanning, artifact verification, reproducible/traceable builds where practical and production-runtime verification.

## 5. Threat Actors

The baseline model includes:

- Anonymous Internet attacker
- Malicious citizen/user
- Malicious authenticated user
- Compromised device
- Cross-case/cross-user attacker
- Malicious administrator/operator
- Insider
- Network attacker
- Malicious document/evidence author or payload
- Compromised Telegram/WhatsApp/Messenger account
- Compromised integration
- Compromised or malicious external provider
- Malicious AI provider/model
- Prompt-injection attacker
- Malicious agent/tool
- Supply-chain attacker

Future threat models may add coordinated abuse, government-side adversarial endpoints, privacy-inference/correlation attackers and other ecosystem-specific actors as the relevant capability becomes real.

## 6. Threat Categories

### T01 — Secret Exposure

Examples: credentials committed to Git, secrets in client bundles, CI logs, Docker layers or error responses.

Required response: detect, revoke/rotate exposed credentials, determine exposure scope, remediate source and history as appropriate, and verify no active copies remain.

### T02 — Broken Object-Level Authorization

Examples: changing a Case ID, Evidence ID or Submission ID to access another user's object.

Required control: authorization must bind the requested object to the authenticated/authorized principal and case context.

### T03 — Privilege Escalation

Examples: client-controlled role fields, forged approval state, expanded agent scopes, unauthorized administrative operations.

Required control: privileges are determined by trusted authorization state, not client claims.

### T04 — Lifecycle Bypass

Examples: submitting before required review, changing a case directly from draft to submitted, skipping consent or approval.

Required control: canonical domain transition rules reject invalid transitions regardless of surface.

### T05 — Evidence Integrity Attack

Examples: replacing an original, altering timestamps/GPS, substituting derivatives, falsifying attestation claims or deleting provenance.

Required control: immutable originals, hashes, provenance records, explicit derivative relationships and truthful implementation claims.

### T06 — Privacy Leakage

Examples: PII in logs, telemetry, URLs, analytics, browser storage, AI context or third-party integrations beyond the authorized purpose.

Required control: data classification, minimization, scoped consent and transmission policy.

### T07 — AI/RAG Manipulation

Examples: prompt injection, malicious retrieved documents, citation manipulation, hallucinated legal claims, cross-user context leakage.

Required control: source/provenance handling, isolation, verification, uncertainty handling and refusal to treat generated claims as verified facts without evidence.

### T08 — Agent Abuse

Examples: an agent sends a message, submits a case, publishes information or calls a privileged tool without the required user authorization.

Required control: model instructions never replace capability authorization; consequential actions require explicit confirmation.

### T09 — Replay/Duplication

Examples: replaying a submission request or repeating a consequential external action after timeout/retry.

Required control: idempotency, request correlation and state-aware authorization for consequential operations.

### T10 — Injection and Malicious Payloads

Examples: SQL injection, XSS, command injection, malicious documents, path traversal or unsafe file processing.

Required control: strict validation, parameterization, safe parsing, content-type/size controls, sandboxing where appropriate and output encoding.

### T11 — Availability/Abuse

Examples: endpoint flooding, expensive AI requests, upload exhaustion, agent loops or repeated submission attempts.

Required control: rate limits, quotas, bounded retries, file limits, timeouts, circuit breakers and cost-aware AI controls.

### T12 — Supply-Chain Compromise

Examples: malicious dependency, compromised GitHub Action, poisoned container base image or leaked build credential.

Required control: dependency pinning/lockfiles, vulnerability review, workflow hardening, secret scanning and release-artifact controls.

## 7. Core Security Invariants

The following are architectural invariants, not UI conventions:

- One user's authorization never implies another user's authorization.
- Authentication never implies authorization to a specific object.
- AI permission never implies action permission.
- Agent instructions never override capability policy.
- Generated content never becomes verified fact merely because a model produced it.
- Original evidence is never silently overwritten by a derivative.
- A provider cannot receive data outside the approved data boundary.
- A surface failure must not unnecessarily cascade into an independent surface.
- Client-controlled state never determines trusted lifecycle/authorization state.
- Hardware-backed/verified/signed claims are made only when technically established.

## 8. Abuse Cases to Test

At minimum, security tests should attempt to:

1. Read another user's Case by changing an identifier.
2. Attach another user's Evidence to a Case.
3. Replace an Evidence original with a derivative.
4. Forge review/approval/submission state.
5. Reuse a consent grant for a different purpose/provider.
6. Cause an AI capability to expose protected context.
7. Trick an agent into invoking an unauthorized tool.
8. Cause a retry to duplicate an external submission.
9. Upload malicious or oversized evidence/document payloads.
10. Exfiltrate secrets through errors/logs/AI responses.
11. Abuse expensive AI or search endpoints for denial-of-service/cost amplification.
12. Bypass rate limits or CORS/security-header controls.
13. Exploit dependency/build workflow compromise.
14. Access protected data through a different Janavani surface.
15. Trigger a consequential action without the required user confirmation.

## 9. Risk Treatment

Findings should be classified by severity and by whether they violate a core invariant. A severe violation of authorization, evidence integrity, secret security, privacy boundary or consequential-action control should block release until remediated or formally accepted by an authorized human decision-maker.

Security work should proceed one verified risk class at a time rather than through speculative broad refactoring.

## 10. Testing Evidence

For each material finding record:

- Threat ID
- Affected capability/surface
- Preconditions
- Reproduction steps
- Expected security property
- Observed behavior
- Severity
- Remediation
- Regression test
- Residual limitation
- Commit/release reference

## 11. Scope Discipline

This baseline does not authorize implementation of every future security idea. New concepts discovered during review should be placed in the Future Ideas Register unless they are necessary to close a verified current risk.

The threat model should evolve when a new capability, provider, access surface, data class or consequential action is introduced.
