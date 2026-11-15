# Environmental Civic Evidence — Product Mapping and Acceptance Contract

**Status:** Proposed product requirements; implementation not asserted  
**Date:** 15 November 2026  
**Scope:** Mapping Janavani's public Environmental Evidence & Citizen Reporting Standard and three environmental guides to existing canonical Civic Case, Evidence, Consent, Authorization, Submission, and Outcome contracts.

## 1. Purpose and governing decision

This document translates the environmental knowledge collection into product requirements. It is a design/review contract, not evidence that a new capability is implemented.

The public guides distinguish five evidence classes: citizen observation; supporting material; independently verified finding; official institutional response; and measured outcome.

These are epistemic and communication distinctions. They are not automatically five CaseStatus values, five database tables, or five capabilities. The implementation must preserve their meaning without expanding the executable lifecycle by analogy.

**Decision:** Compose existing canonical capabilities. Do not create a parallel case, evidence, consent, or submission subsystem.

## 2. Existing contracts to reuse

Repository review identified these existing contracts:

- `src/core/civic_case.py` and the canonical Civic Case capability.
- `src/capabilities/evidence.py` and the provider-neutral Evidence boundary.
- `docs/architecture/CITIZEN_EVIDENCE_BOUNDARY_CONTRACT.md`.
- `docs/architecture/CANONICAL_CASE_POSTGRES_SCHEMA.md`.
- `docs/architecture/CASE_LIFECYCLE_SEMANTICS.md`.
- `docs/EVIDENCE_PROVENANCE_CONVERGENCE_2026-09-09.md`.
- Existing Consent, Authorization, Submission, Follow-up and Outcome capabilities.

The existing Evidence contract separates binary media from metadata. Evidence registration does not mean upload, transmission, or publication. Preserve that boundary.

## 3. Semantic model

The Civic Case lifecycle answers: **what is the operational state of this case?**

The environmental evidence record answers: **what is known, what is claimed, what supports it, who assessed it, and what remains uncertain?**

Do not collapse these into one status field.

| Public-facing class | Meaning | Minimum provenance |
|---|---|---|
| Citizen observation | A person's account of what they directly saw, heard or experienced | Source category, observation time if known, approximate location/jurisdiction, original wording, submission time |
| Supporting material | Material offered to support or contextualise an observation | Evidence ID, source, capture time if known, hash where applicable, transformations, consent/access/retention metadata |
| Independently verified finding | A bounded finding reached through documented review appropriate to the question | Reviewer/competence or responsible institution, method, sources examined, scope, time, limitations, result and review timestamp |
| Official institutional response | Statement, notice, record or action attributable to an identified public institution | Institution, office, source channel, reference number if available, date, original source and authentication status |
| Measured outcome | A change assessed against a stated baseline and method | Indicator, baseline, method, period, source, uncertainty, assessor and limitations |

An official response is not automatically independent verification. A citizen observation is not automatically a finding. A recorded action is not automatically a successful outcome.

## 4. Environmental case requirements

The use case may include waterbody and wetland concerns; drainage obstruction, urban waterlogging and flood-related public-service concerns; and forest, biodiversity and ecological-restoration concerns.

Do not hard-code these as new `CaseType` values until the canonical case taxonomy and routing registry have been checked. Unknown or disputed jurisdiction must remain explicitly unknown; the product must not guess an authority.

## 5. Evidence, privacy and consent

1. Raw photographs, video and documents remain citizen-controlled/local by default, consistent with the Citizen Evidence Boundary Contract.
2. Camera/file permission is not consent to transmit, retain, publish or use material for unrelated purposes.
3. Before upload, show what will be transmitted, purpose, destination, access scope and retention implications.
4. Minimise unnecessary EXIF, precise location, faces, voices, contact details and unrelated personal information.
5. Preserve source and transformation history where evidence retention is explicitly chosen and permitted.
6. Evidence registration or attachment must not silently upload binary content.
7. Public display is a separate, purpose-bound, consent-aware decision; private evidence is not public by default.
8. Sensitive ecological locations, threatened species locations, Indigenous/community knowledge, private land and safety-sensitive observations require risk assessment and minimisation. Do not expose precise coordinates by default.
9. Consent must be purpose- and scope-specific, revocable where applicable, and rechecked for consequential use.
10. Access, correction, retention, deletion and legal-hold behaviour must follow canonical privacy, storage and consent contracts. This document invents no retention period.

## 6. Verification record

A verification record must be question-specific and bounded. Capture:

- The precise question and claim assessed.
- Evidence and sources actually examined.
- Method and relevant limitations.
- Who or what performed the review (human, institution, automated process), with attribution.
- Review date and version.
- Result, such as supported, not supported, inconclusive, conflicting or outside scope, subject to canonical enum review before implementation.
- Corrections, superseding reviews and audit history.

AI-assisted extraction, translation, classification or summarisation is an analytical aid. It must preserve source links and uncertainty and must never self-upgrade a claim to an independently verified finding. Do not fabricate reviewer identity, qualification or institutional authority.

## 7. Official response, routing and submission

- Use the existing authority/destination registry and capability contracts.
- Preserve distinctions between suggested authority, verified destination, submission attempt, transport result, external acknowledgement, authority response and independently assessed action.
- Acknowledgement does not prove processing has begun. A response does not prove the claim or resolution.
- Do not infer responsibility from proximity alone; check jurisdiction and remit.
- Record the original official source and reference number when available.
- Do not auto-submit RTI requests, complaints or other consequential communications without the existing explicit user review and approval gate.

## 8. Outcome assessment

Outcome assessment is a separate evidentiary activity, not a synonym for case closure. Where appropriate, record intended outcome and indicator; baseline and observation period; method and source; who supplied or performed the measurement; comparability constraints and uncertainty; and whether the result is reported, independently assessed or institutionally certified.

A case may be closed under the canonical lifecycle without claiming an ecological or public-service outcome has been achieved. A measured improvement must not silently mutate the case lifecycle.

## 9. Public presentation

Public case views, dashboards and reports must label citizen claims as claims/observations; distinguish submitted material from material reviewed by Janavani; state who performed verification and its scope; attribute official responses to their source; separate action reported from outcome measured; show dates and correction history; expose uncertainty and missing information; avoid unsupported defamatory or conclusory language; and apply privacy, consent, redaction and sensitive-location safeguards.

Aggregate statistics must disclose denominators, coverage, missingness and methodology. Counts of reports, responses or actions must not be represented as counts of verified problems or successful resolutions.

## 10. Surface independence

Web, Android, iOS, Telegram, WhatsApp, Messenger and future surfaces must call shared capabilities and policy boundaries. No surface may implement its own evidence classification, verification authority, consent logic, case transitions or authority routing. A channel outage must not corrupt the underlying case or evidence record.

## 11. Acceptance criteria

The environmental evidence vertical slice is not production-ready until tests demonstrate:

1. A citizen observation can be recorded without being labelled verified.
2. Evidence metadata is registered and attached through the canonical Evidence capability.
3. Registration does not imply raw-media upload or public publication.
4. Consent is explicit, scoped, recorded and rechecked for consequential use.
5. Provenance and transformation history survive persistence and retrieval.
6. Verification identifies question, method, sources, assessor, scope and limitations.
7. AI analysis cannot independently create a verified finding or official response.
8. Official responses are source-attributed and distinct from acknowledgement and outcome.
9. Submission attempts, transport results, acknowledgement and authority response remain distinct.
10. Outcome assessment records baseline, method and period and does not silently mutate case lifecycle.
11. Access control prevents cross-owner and unauthorised public access.
12. Redaction and sensitive-location controls are tested.
13. Corrections and superseding assessments preserve audit history.
14. The same domain behaviour is exercised through at least two independent adapters without duplicated business logic.
15. Repository CI evidence is captured before implementation is called complete.

## 12. Explicit non-goals

This contract does not create a second Evidence capability or case repository; add the five public evidence classes as CaseStatus values; claim Janavani currently verifies environmental allegations; claim government integrations or automated authority feeds exist; establish legal conclusions or expert ecological determinations; define universal retention or public disclosure policy; authorise public evidence publication by default; or replace specialist review and competent authorities.

## 13. Implementation sequence

1. Map each requirement to exact current domain type, capability, persistence contract and test; mark verified, partial, absent or not yet inspected.
2. Confirm whether existing EvidenceObject, provenance, case events, consent, authority, response and outcome contracts represent the facts without semantic overloading.
3. Write focused contract tests for gaps before production code changes.
4. Implement only the smallest additive change through canonical capabilities and providers.
5. Verify privacy/RLS, cross-owner isolation, retention and audit behaviour.
6. Verify the vertical slice across independent surfaces and capture CI evidence.
7. Update public practice notes only after product behaviour and policy are implemented.

## 14. Decision

Adopt this as a proposed product-mapping and acceptance contract for design/review. It is not evidence that any new product capability is implemented. Existing canonical domain and provider contracts remain authoritative until a reviewed change is approved and verified.
