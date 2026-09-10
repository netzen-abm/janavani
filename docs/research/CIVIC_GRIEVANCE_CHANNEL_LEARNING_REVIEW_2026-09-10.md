# Civic Grievance Channel Learning Review — 2026-09-10

## Purpose

This document evaluates the supplied research on Bengaluru Sahaaya/Fix Pothole channels and national grievance channels from the **citizen perspective**.

This is comparative research, not a Janavani product specification. Janavani must remain an independent civic-infrastructure system. No external portal, application, workflow, terminology, government process, or technology is adopted merely because it exists elsewhere.

## Executive conclusion

Existing civic grievance systems demonstrate that digital complaint registration, geolocation, routing, status tracking, escalation, multilingual access, and operational dashboards are useful. They also expose a deeper citizen problem: **registration is not the same as resolution, and official closure is not the same as citizen-confirmed resolution**.

The strongest lesson for Janavani is therefore not "build a better Sahaaya". It is:

> Build a citizen-controlled civic-action record that can help a person understand the problem, preserve evidence, identify the responsible authority, choose an appropriate official channel, act, retain proof of what happened, follow up, and challenge an incorrect outcome.

## What appears useful in the supplied research

### 1. Multiple channels are unavoidable

Sahaaya, Fix Pothole, Rajmargyatra, Meri Sadak and CPGRAMS illustrate that responsibility is distributed by jurisdiction, department and road/service class.

**Lesson:** citizens need help determining *where an issue belongs*.

**Potential Janavani learning:** authority discovery and jurisdiction reasoning are first-class capabilities.

**Do not adopt:** a single hard-coded government routing hierarchy.

### 2. Location and evidence materially improve civic reports

Pothole workflows demonstrate the value of photographs, GPS/location and operational routing.

**Lesson:** a citizen should not have to describe a physical defect entirely in words when the device can capture useful evidence.

**Potential Janavani learning:** evidence capture should support media, location, time, integrity and provenance.

**Correction:** AI- or device-derived measurements are observations, not automatically authoritative facts.

### 3. Tracking creates continuity

Government grievance systems show the value of complaint numbers, status changes and escalation paths.

**Lesson:** citizens need a persistent record instead of repeatedly explaining the same problem.

**Potential Janavani learning:** canonical Case + lifecycle timeline + follow-up.

**Correction:** the timeline must distinguish citizen observations, authority assertions, transport events, acknowledgements, responses and verified outcomes.

### 4. Escalation is essential

The supplied research highlights escalation and reopening as important responses to unresolved complaints.

**Lesson:** a citizen needs a path after the first submission fails.

**Potential Janavani learning:** follow-up and escalation should be explicit capabilities, not ad-hoc messages.

**Correction:** escalation must be jurisdiction-aware and evidence-based; Janavani should not automatically escalate every case.

### 5. Citizen confirmation is a major accountability improvement

The reported Sahaaya 3.0 direction is especially instructive: citizen confirmation/reopening addresses the gap between administrative closure and lived resolution.

**Lesson:** closure should not be treated as a single authority-controlled fact.

**Potential Janavani learning:** represent at least two distinct concepts:

- authority-reported resolution;
- citizen-confirmed outcome.

A disagreement should remain visible rather than being overwritten.

## What Janavani should NOT copy blindly

### Government portal architecture

Janavani should not become a mirror of Sahaaya, BBMP, NHAI, PMGSY or CPGRAMS internal workflows.

### Government-controlled closure semantics

An external system's `closed` state must never overwrite Janavani's citizen-side understanding of the case.

### Provider-specific identifiers as the canonical Case ID

External complaint numbers should be recorded as external references, not replace the canonical Janavani Case identity.

### AI as authority

AI pothole detection, dimension estimation, classification or contractor matching can be useful assistance. They must carry uncertainty/provenance and remain distinguishable from verified facts.

### Hard-coded contact numbers

Government phone/WhatsApp/app details change. Janavani should maintain source, verification date and jurisdiction for external channel information rather than treating copied contact details as permanent truth.

### One-channel dependency

A citizen should not lose their case because a government portal, messaging service or Janavani access surface is unavailable.

## Citizen-angle gap analysis

| Citizen problem | Existing-channel lesson | Janavani design response |
|---|---|---|
| I don't know whom to contact | Routing is fragmented | Authority discovery + explain why |
| I don't know what to say | Forms assume knowledge | Guided issue structuring |
| I have proof but fear losing it | Media is attached to complaints | Citizen-controlled evidence + provenance |
| I don't know whether my submission actually arrived | Status can be ambiguous | Explicit transport/receipt/acknowledgement states |
| They marked it resolved but it isn't | Closure may be administrative | Separate authority resolution from citizen confirmation |
| I need to reopen it | Reopening differs by system | Case follow-up/reopen capability |
| I need to escalate | Escalation is fragmented | Evidence-backed, jurisdiction-aware escalation guidance |
| The portal is unavailable | Channel availability varies | Preserve case locally and support alternate channels |
| I don't trust an AI-generated claim | AI can be wrong | Provenance, uncertainty, user review, deterministic fallback |
| I fear exposing sensitive information | External systems may require transmission | Data minimization, explicit consent, user-controlled evidence |
| I have used several channels | Systems are fragmented | One canonical citizen Case with external references |
| I don't understand what happened | Status codes are opaque | Plain-language lifecycle explanation |

## The key distinction

Janavani should be the **citizen-side continuity and agency layer**, not another government grievance department and not a replacement government database.

Conceptually:

```text
REAL-WORLD PROBLEM
       ↓
CITIZEN-CONTROLLED CASE
       ↓
FACTS + EVIDENCE + PROVENANCE
       ↓
AUTHORITY DISCOVERY
       ↓
ACTION / DOCUMENT
       ↓
CITIZEN REVIEW + APPROVAL
       ↓
APPROPRIATE EXTERNAL CHANNEL
       ↓
TRANSPORT RECEIPT
       ↓
INDEPENDENT ACKNOWLEDGEMENT EVIDENCE
       ↓
FOLLOW-UP
       ↓
AUTHORITY-REPORTED OUTCOME
       ↓
CITIZEN VERIFICATION
       ↓
REOPEN / ESCALATE / ACCEPT
```

The external government channel remains an external system. Janavani preserves the citizen's continuity around it.

## What this research changes in our engineering priorities

### Increase priority

1. Authority discovery and verification.
2. Evidence capture and provenance.
3. Explicit external-channel registry with source/verification metadata.
4. Submission/transport/acknowledgement separation.
5. Follow-up, reopen and escalation semantics.
6. Citizen-vs-authority outcome distinction.
7. Plain-language explanations of case state.
8. Alternate-channel resilience.
9. User-controlled local case continuity.
10. Measurement of citizen effort and successful outcomes.

### Keep constrained

- AI automation of consequential actions.
- Automatic escalation.
- Contractor attribution without authoritative supporting data.
- AI-derived measurements presented as verified measurements.
- Broad scraping or copying of government contact data without provenance.
- Building a separate Janavani feature for every government portal.

## Pothole vertical as a test case, not product identity

Potholes are an excellent test case because they combine location, media evidence, authority discovery, external routing, repair verification and citizen confirmation.

They should be treated as a **vertical slice for validating the general civic-action architecture**, not as a reason to turn Janavani into a pothole application.

The same architecture should later support garbage, streetlights, drainage, public safety, RTI, petitions, representations and other civic actions without duplicating the underlying Case/Evidence/Authority/Document/Submission model.

## Research discipline

External facts must be classified as:

- verified official fact;
- credible reported fact;
- citizen/community report;
- model inference;
- hypothesis;
- unverified contact/channel information.

Janavani must not convert a research claim into a canonical domain fact without an appropriate verification path.

## Relationship to existing Janavani architecture

This review reinforces existing architectural principles rather than replacing them:

- Case is canonical.
- Evidence is separate from Case narrative.
- Provenance matters.
- Consent is explicit where required.
- Document generation is separate from submission.
- Transport is an adapter, not domain authority.
- Acknowledgement requires evidence.
- Access surfaces are independent consumers of shared capabilities.
- AI is optional and must fail safely.
- Provider/channel failure must not destroy the underlying citizen Case.

## Decision

**LEARN — DO NOT INCORPORATE EXTERNALLY OWNED PRODUCT IDENTITY.**

Use these systems as empirical reference points for identifying citizen pain, operational constraints, useful patterns and failure modes. Janavani remains independently defined by its own civic-infrastructure principles and canonical contracts.

## Recommended next implementation

Complete the provider-neutral delivery boundary, then integrate it with the canonical SubmissionCapability and EvidenceRepository so the system can distinguish:

`prepared → attempted → submitted → acknowledged-with-evidence → authority-response → citizen-verified-outcome`.

Only after that should the first citizen-facing broken-road vertical slice be completed and tested end-to-end.
