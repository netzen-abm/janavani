# Ecosystem Security Invariants

**Status:** Canonical architecture contract

## Purpose

Define security properties that every Janavani access surface and every future ecosystem application must inherit from shared infrastructure rather than reimplement independently.

## 1. Surface independence

Web, Telegram, WhatsApp, mobile, DApp, Mini App and future surfaces are independently deployable. A surface may fail without disabling another surface.

A surface must never become the owner of shared identity, Case, Evidence, Authority, Consent, authorization, submission, storage, or provider-selection logic.

## 2. Capability boundary

Every reusable action is exposed through a capability contract. The capability boundary is responsible for identity context, authorization, consent where required, purpose and scope, safety/risk classification, provenance, idempotency for external side effects, truthful outcome reporting, and audit evidence.

Access surfaces only translate interaction into capability requests.

## 3. Least privilege

Permissions and capabilities are granted only for the declared purpose and scope. A capability must not silently broaden data access, device access, identity scope, geographic access, external side effects, or retention period.

## 4. Purpose-bound device access

Camera, microphone, location, contacts, files and similar device resources are purpose-bound.

Lifecycle: Declare purpose -> request permission -> use resource -> release/disable access when finished.

Where the platform supports explicit release/revocation, the adapter must perform it after the purpose is complete. A later use requires a valid permission state again.

## 5. Provider isolation

Domain and capability code depend on provider contracts. Concrete providers for databases, object storage, Redis, AI, messaging, identity and external services are selected at composition/runtime boundaries.

No access surface may instantiate a concrete provider for shared business state directly.

## 6. Protected-data boundary

Protected data must cross an explicit authorization boundary. Default deny; owner/resource checks before mutation; no authorization based only on a surface identifier; no direct protected-data access from transport handlers; negative authorization paths are mandatory tests; logs and audit records minimize personal data.

## 7. Consent is executable state

Consent is not merely UI text. Where an action requires consent, the capability must verify the applicable consent reference, purpose and scope at execution time.

Consequential actions must fail closed when required consent is absent, invalid, expired or outside scope.

## 8. External side effects

External side effects require an execution envelope containing capability identifier, action, identity, surface, correlation identifier, risk level, authorization reference, consent references where applicable, idempotency key, provenance, and truthful result.

The domain must never report an external action as successful merely because a request object was constructed.

## 9. Transaction boundary

Coupled state changes must use an explicit transaction or Unit-of-Work contract. Case mutation + Submission state + Case event must commit atomically where the provider supports the required durability boundary.

External delivery is not silently equated with database commit.

## 10. Provenance and trust

Evidence and externally sourced information carry provenance. The system distinguishes citizen-provided, authoritative, system-derived, expert-reviewed, AI-generated, and unverified information.

AI-generated or transformed information must not silently become authoritative evidence.

## 11. Ephemeral-state discipline

Ephemeral state is explicitly scoped by task/session. Sensitive transient state has a defined destruction/revocation boundary. Security-sensitive cleanup must return a truthful result and must not claim destruction when the provider operation failed.

## 12. Observability

Security and consequential capabilities emit sufficient audit evidence to reconstruct: who requested what, under which policy/consent, against which resource, what provider acted, and what actually happened.

Audit data itself follows data-minimisation and retention rules.

## 13. Branch and source hygiene

Only the nine sanctioned long-lived branches are development roles. Historical work follows: AUDIT -> EXTRACT -> CONVERGE -> VERIFY -> ARCHIVE EVIDENCE -> DELETE.

Historical branches must never become a second architectural authority.

## 14. Ecosystem readiness gate

A shared capability is ecosystem-ready only when: the contract is provider-neutral; authorization is enforced at the capability boundary; consent is enforced where applicable; purpose/scope are explicit; provenance is preserved; external side effects are idempotent where applicable; negative security paths are tested; at least two independent surfaces can consume it without duplicating domain logic; provider selection remains outside the surface; and security-sensitive failure is fail-closed.

## Canonical flow

Surface -> Identity Context -> Capability Gateway -> Authorization + Consent + Safety -> Execution Envelope -> Shared Capability -> Provider Contract -> Provider -> Truthful Result + Audit Evidence

This contract is infrastructure-level so future applications in other domains can reuse the same security model without inheriting Janavani-specific transport or UI assumptions.
