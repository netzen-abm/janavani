# JANAVANI — External Tool Reuse, Verification & Delegation Contract

Status: Proposed canonical architecture contract
Scope: Shared ecosystem infrastructure
Principle: Reuse before reinventing; delegate when an existing system is the authoritative service owner.

## 1. Decision

Janavani MUST NOT build a Janavani-native replacement for an existing service merely because Janavani can reproduce its interface or workflow.

When an existing service is authoritative, mature, legally responsible for the transaction, or already provides a capability that Janavani does not need to own, Janavani SHOULD prefer:

1. Inform / link-out.
2. Guided handoff: prepare citizen-side material, then let the citizen complete the external operation.
3. Deep-link handoff when the destination officially supports it.
4. Artifact handoff: generate a document/evidence package for user upload.
5. Provider adapter when an official API or SDK exists and continuity materially benefits the citizen.
6. Embedded integration only when necessary and explicitly permitted.

The default is delegation, not imitation.

## 2. What Janavani owns

Janavani owns the citizen-side orchestration layer: issue understanding, case structure, evidence/provenance, authority discovery, document preparation, privacy/data minimization, consent/authorization, user review, handoff explanation, truthful status, and return-to-Janavani tracking where technically possible.

Janavani does NOT automatically own the external authority transaction, database, adjudication, authentication, or official record.

## 3. External-service verification

Before Janavani presents an external service as an official destination, it SHOULD maintain: canonical service name, official owner, verified official domain, purpose/scope, jurisdiction, prerequisites, authentication requirements, supported citizen action, fees if any, attachment support, deep-link/prefill support, privacy implications, accessibility/language information where known, last verification timestamp, verification source, and fallback route.

A reachable URL is not sufficient evidence that it is the correct official service.

## 4. Truthful handoff states

Use explicit states such as:

- RECOMMENDED
- VERIFIED_DESTINATION
- READY_FOR_HANDOFF
- HANDED_OFF
- USER_CONTINUING_EXTERNALLY
- CONFIRMED_BY_EXTERNAL_SERVICE
- UNKNOWN
- FAILED

Janavani MUST NOT report external submission success merely because a browser opened.

## 5. Privacy and authentication

Opening an external website is not permission to transmit Janavani data to it.

Preferred flow:

Janavani local data → minimize → user review → explicit choice → external handoff

Janavani SHOULD NOT collect or proxy external credentials. Prefer direct citizen authentication at the external service. CAPTCHA, OTP, MFA, Aadhaar/PAN authentication, payment and similar controls remain with the external service unless an official integration explicitly supports them.

## 6. Reuse order

Before implementing automation, evaluate in this order:

1. Official API or SDK.
2. Official supported deep-link or handoff.
3. Official importable/downloadable artifact.
4. Human-guided browser handoff.
5. Browser automation only when explicitly permitted and operationally justified.
6. Scraping only for lawful research/data-ingestion use, never as an assumed transaction mechanism.

Respect terms, rate limits, access controls, authentication, privacy and copyright.

## 7. Build-versus-reuse test

Build a Janavani-native layer only when no suitable external service exists, the capability is a core Janavani differentiator, interoperability requires a neutral layer, the external service cannot provide the needed citizen workflow, accessibility/privacy/local-first requirements require ownership, an official API makes a stable adapter materially useful, or Janavani must preserve a cross-service case/evidence/provenance lifecycle.

Even then, build the smallest missing layer rather than recreating the external system.

## 8. AI and agents

AI may classify needs, explain service differences, identify likely jurisdiction, prepare drafts, compare known prerequisites and suggest a destination.

AI MUST NOT invent official URLs, departments, submission success, acknowledgement numbers, legal authority, eligibility or service availability.

External-service selection SHOULD be grounded in a verified service registry, not model memory.

Agentic AI may invoke service-discovery or handoff tools only through the existing privacy, authorization, tool-policy and consequential-action gates.

## 9. Case-study lessons

The supplied research supports a consistent pattern: specialized authoritative tools should remain authoritative; Janavani should add citizen-side orchestration, context, privacy, reviewability and interoperability.

The atmospheric-observation material also reinforces the evidence principle: a specialized data source should be treated as an evidence provider, not silently promoted into a conclusion. Aircraft telemetry or patterns alone do not establish weather modification activity.

General rule:

Use the strongest existing source for the fact or transaction; use Janavani to make the citizen path understandable, privacy-preserving, reviewable and interoperable.

## 10. Existing Indian services worth delegating to

CPGRAMS: central public grievance handling. Janavani should route eligible public-service grievances rather than recreate the submission system.

RTI Online: Central Government RTI requests and first appeals. Janavani must check jurisdiction first because the portal states that State Government public authorities should not use it.

National Consumer Helpline: consumer grievance registration through web, app, UMANG and WhatsApp. Janavani can classify the problem and route the citizen to the appropriate channel.

eCourts: court case status, cause lists, orders/judgments and other court services. Janavani should not duplicate the court record system.

DigiLocker: government digital document access, sharing and verification. Janavani should prefer handoff or permitted integration rather than unnecessary duplication of authoritative documents.

These are examples, not an exhaustive registry.

## 11. Handoff UX

When delegating, show the citizen:

1. Why the service is relevant.
2. Who operates it.
3. What Janavani prepared.
4. What information will leave Janavani, if any.
5. What the citizen must do externally.
6. What Janavani can and cannot track.
7. The verified official destination.
8. A manual fallback.

## 12. Implementation boundary

Do NOT create a giant generic external-tools subsystem yet.

First implement the smallest reusable primitives:

Verified Service Record → Scope Check → Handoff Decision → Privacy/Authorization → User Choice → External Destination Adapter → Truthful Handoff State

A future provider-neutral adapter may expose discover, verify, prepare_handoff, handoff and reconcile operations. Concrete adapters should be added only after a specific service has a documented need and supported integration path.

## 13. Relationship to existing Janavani architecture

This contract extends existing architecture. The Capability Registry remains the capability index. Case remains the citizen lifecycle owner. Document, Evidence and Authority remain their respective owners. Privacy/Safety, Authorization and Consequential Operation remain the policy boundaries. Surface adapters remain consumers. Provider-neutral composition remains mandatory.

No surface may bypass these boundaries merely because an external service is being used.

## 14. Non-goals

This contract does not authorize credential collection, CAPTCHA bypass, OTP/MFA interception, unauthorized scraping, silent browser automation, false submission claims, automatic legal advice, copying government databases without permission, or replacing authoritative government systems without a justified capability gap.

## 15. Recommended product position

Janavani should become a citizen orchestration and interoperability layer, not another collection of government portals.

Citizen intent → understand → verify → prepare → protect → hand off → track what can truthfully be tracked

That is the governing build-versus-reuse principle for the ecosystem.