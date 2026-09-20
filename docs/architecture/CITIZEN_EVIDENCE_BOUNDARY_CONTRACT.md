# Janavani Citizen Evidence Boundary Contract

**Status:** Proposed canonical architecture contract  
**Scope:** Citizen-submitted evidence, with initial application to the Atmospheric Activity & Weather-Modification Evidence Observatory  
**Related issue:** #175

## 1. Purpose

Define the boundary between evidence a citizen controls on their device and evidence Janavani may retain as shared platform state.

The contract is intentionally capability-level and surface-neutral. WebApp, Android, iOS, Telegram Mini App and future surfaces must consume the same boundary rather than implement separate upload/privacy logic.

## 2. Core principle

> **Citizen-owned raw evidence. Janavani-owned evidence structure.**

Raw photographs and videos remain on the citizen's device by default. Janavani may retain only the minimum evidence representation necessary for an explicitly requested capability.

## 3. Evidence lifecycle

```text
Citizen observation
    ↓
Local capture / local file selection
    ↓
Privacy + Sensitive Observation Gate
    ↓
Local analysis where supported
    ↓
User review of proposed derived information
    ↓
Explicit upload decision
    ↓
Minimal evidence registration
    ↓
Existing EvidenceCapability
    ↓
EvidenceRepository / provider boundary
    ↓
Case or observation relationship
```

No step may silently transmit the raw media.

## 4. Raw-media boundary

Raw media is **local by default**.

Janavani clients MUST NOT:

- upload camera media merely because camera access was granted;
- upload media in the background without explicit user action;
- retain a raw copy when a derived representation satisfies the requested capability;
- expose raw media publicly by default;
- use raw media for unrelated analytics or model training without a separate lawful, explicit capability and consent model.

If the user explicitly chooses upload, the client must show what will be transmitted before confirmation.

## 5. Privacy minimisation

Before optional transmission, the client should remove or avoid unnecessary:

- EXIF metadata;
- precise GPS coordinates;
- device identifiers;
- faces and voices unrelated to the requested evidence;
- contacts or address-book data;
- unrelated images/media;
- continuous location history;
- personal names, phone numbers and email addresses unless explicitly required by the requested capability.

The default observation location should be no more precise than necessary for the capability. Exact home coordinates must not be collected merely to verify an atmospheric observation.

## 6. Sensitive observation gate

A shared safety/privacy gate must execute before evidence is retained by Janavani.

The gate must distinguish at minimum:

- **ALLOW** — ordinary, relevant public observation;
- **MINIMIZE** — relevant evidence requiring removal/aggregation of unnecessary data;
- **BLOCK** — sensitive government/military/security information or other prohibited material;
- **REVIEW** — ambiguous material requiring human or policy review.

The gate must not be implemented independently by each surface.

## 7. Derived evidence

Derived evidence may include only information necessary for the requested verification, for example:

- observation timestamp;
- approximate observation area;
- user-provided description;
- non-sensitive visual characteristics;
- selected frame or crop where necessary;
- cryptographic hash of the original when the user explicitly chooses evidence preservation.

A model-generated description is an analytical output, not automatically a verified fact.

## 8. Existing Evidence infrastructure

The repository already defines a provider-neutral `EvidenceObject`, `EvidenceRepository`, `EvidenceSource`, SHA-256 validation and `EvidenceCapability`. The new citizen flow must use those primitives rather than creating a second evidence repository or capability.

The current Evidence contract represents binary content through `storage_ref` plus hash and leaves storage implementation to provider adapters. This contract therefore treats `storage_ref` as an implementation boundary, not permission to upload raw media by default.

## 9. Provenance

Retained evidence must preserve provenance sufficient to understand:

- what was observed;
- when it was captured or received;
- how it entered Janavani;
- whether it was user-supplied or externally sourced;
- what transformations occurred before registration;
- what source/provider supplied external observations;
- what verification state currently applies.

Transformation metadata must not be represented as proof of the original observation.

## 10. Evidence states

The Atmospheric Observatory uses the following epistemic states:

- **OBSERVED** — directly measured/publicly sourced observation;
- **DOCUMENTED** — supported by an official/public record;
- **CORRELATED** — independent observations align in time/location; causation is not established;
- **HYPOTHESIS** — analytical lead requiring verification;
- **VERIFIED ACTIVITY** — documentary and independent observational evidence corroborate the activity.

Citizen media alone must not elevate an atmospheric event to `VERIFIED ACTIVITY`.

## 11. User control

The user must be able to:

1. inspect the proposed evidence package before upload;
2. decline upload;
3. cancel before transmission;
4. understand whether raw media or derived evidence will be transmitted;
5. edit the description and non-sensitive metadata;
6. request deletion of retained derived evidence where the applicable retention contract permits it.

No capability may treat camera permission as evidence-submission consent.

## 12. RTI boundary

Citizen evidence may inform an evidence gap used by the RTI Draft Generator, but it must never trigger direct RTI submission.

The output sequence remains:

```text
Evidence gap
    ↓
RTI draft
    ↓
User review/edit
    ↓
PDF/DOCX export
    ↓
User independently submits
```

Applicant identity fields remain user-controlled and should be placeholders unless explicitly supplied for document generation.

## 13. Surface independence

Every access surface must enforce the same contract:

```text
Surface adapter
    ↓
Citizen Evidence capability contract
    ↓
Safety/Privacy gate
    ↓
Canonical Evidence capability
    ↓
Shared repository/provider boundary
```

Telegram, WebApp, Android, iOS and other surfaces must not create channel-specific evidence schemas, storage paths or privacy exceptions.

## 14. Security and misuse constraints

The capability must not be used to:

- identify or track individuals;
- identify aircraft occupants;
- expose sensitive government/military operations;
- construct unrestricted personal movement histories;
- infer private identity from media or telemetry;
- automate allegations against an operator, person or institution;
- bypass provider access controls or aviation/security restrictions.

## 15. Retention

Raw citizen media is not a Janavani server-side default.

If raw media is voluntarily uploaded because a specific capability genuinely requires it, the retention purpose, retention period and access policy must be established before implementation. Otherwise, prefer derived/minimized evidence and retain only the metadata necessary for the declared purpose.

## 16. Implementation gates

Before production implementation:

- map the contract to the existing EvidenceCapability and EvidenceRepository;
- define the Sensitive Observation Gate interface;
- define deterministic metadata-minimisation behavior;
- define client-side confirmation UX contract;
- define provenance/transformation representation;
- add negative tests for silent upload, excessive metadata, sensitive-data retention and attribution escalation;
- verify that no access surface bypasses the canonical capability;
- reuse existing document export and RTI draft infrastructure.

No new production database, object-storage provider, aircraft provider or AI vision provider is required by this contract.

## 17. Non-goals

This contract does not authorize or implement:

- live aircraft tracking;
- historical aircraft movement databases;
- automatic geoengineering detection;
- government/military aircraft intelligence;
- direct RTI submission;
- autonomous public accusations;
- mandatory cloud storage of citizen media.

## 18. Completion criterion

This contract is satisfied only when the implemented capability can demonstrate that raw media remains local by default, every transmission is explicit, retained evidence is minimized and provenance-aware, sensitive observations are filtered, all surfaces use the canonical boundary, and RTI output remains generation-only.
