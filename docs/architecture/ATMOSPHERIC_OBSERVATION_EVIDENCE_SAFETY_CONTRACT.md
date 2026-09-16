# Janavani Atmospheric Observation, Evidence & Safety Contract

**Status:** Proposed canonical architecture contract
**Scope:** Atmospheric Activity & Weather-Modification Evidence Observatory
**Related issue:** #175

## 1. Purpose

Janavani may provide privacy-preserving public evidence infrastructure for observing aviation, meteorological, atmospheric-research and documented weather-modification activity in India.

The system informs citizens; it does not determine mission purpose from flight patterns and does not make accusations or attributions without corroborating evidence.

## 2. Core epistemic rule

Aircraft type, registration, callsign, route, altitude, loitering, grid/orbit pattern, contrail, cloud appearance, radar feature, rainfall anomaly or satellite observation MUST NOT by itself be labelled as geoengineering, weather modification, cloud seeding, military activity or government activity.

Every observation must retain its evidence state:

- OBSERVED — directly measured/publicly sourced observation.
- DOCUMENTED — supported by an official/public record.
- CORRELATED — independent observations align in time/location; causation is not established.
- HYPOTHESIS — an analytical lead requiring verification.
- VERIFIED ACTIVITY — documentary evidence and independent observational evidence corroborate the activity.

## 3. Government and sensitive aviation-data boundary

Janavani MUST NOT intentionally ingest, retain, expose, enrich or publish sensitive government aviation information, classified/restricted information, military operational information, security-sensitive routes, protected aircraft details, restricted telemetry or non-public government datasets.

Public availability does not automatically make information appropriate for Janavani publication. Sources must be evaluated for lawful access, terms, privacy, aviation/security implications and whether publication creates unnecessary operational risk.

Military/government aircraft MUST NOT receive a special tracking or attribution mode merely because they appear in an open feed. Where a public source contains potentially sensitive information, Janavani should minimize, suppress, aggregate or discard it according to policy.

## 4. Data minimization and local-first media capture

Citizen-submitted photographs and videos are local-first evidence.

Default behavior:

1. Camera capture occurs on the user's device.
2. The original/raw file remains on the user's device unless the user explicitly chooses to upload it.
3. Janavani must not silently upload camera media.
4. The system should extract only the minimum information required for the requested verification.
5. EXIF/GPS metadata, device identifiers, faces, voices, contact information and other unnecessary personal data should be stripped or avoided before any optional upload where technically feasible.
6. The user must see what will be uploaded before confirmation.
7. Upload is optional and revocable where technically feasible.
8. A user may perform local analysis without uploading the original media whenever supported.

## 5. Minimal evidence submission

For an optional evidence submission, prefer:

- approximate observation area selected by the user;
- observation date/time;
- optional user-entered description;
- derived visual features necessary for verification;
- cryptographic hash of the original only when the user chooses an evidence-preservation workflow.

Do not collect names, phone numbers, email addresses, precise home location, contacts, unrelated photos, continuous location history, microphone recordings, device identifiers or biometric information unless a separately justified and explicitly consented capability requires it.

## 6. No direct RTI submission

Janavani MUST NOT submit RTI applications on the user's behalf.

Janavani may generate a reviewable RTI draft from documented evidence gaps. The user remains the requester and decision-maker.

The generated draft must be exportable as PDF and/or DOCX. The user downloads/reviews it and independently submits it through the appropriate lawful channel.

The generated RTI should request records rather than assert conclusions. It should identify the relevant authority, date/area scope, records sought and known evidence gap. It must not include unnecessary personal information or unsupported allegations.

## 7. Evidence correlation

Correlation may combine independently sourced public observations such as:

- lawful public aircraft telemetry;
- public meteorological observations;
- IMD radar/weather products;
- public satellite observations;
- public lightning/environmental observations;
- publicly available official permissions, notices, tenders, reports or project records.

Provider-specific APIs must be adapters behind provider-neutral contracts. No surface may directly call a provider.

## 8. Alert policy

Citizen alerts must distinguish:

- observation;
- documented activity;
- correlation;
- unresolved hypothesis;
- verified activity.

Alerts must never use sensational language or imply causation from correlation. Government/private attribution requires documentary support and must be explicitly sourced.

## 9. Abuse prevention

The observatory MUST NOT provide capabilities intended to:

- identify or expose sensitive government/military operations;
- facilitate stalking or targeting of individuals or aircraft occupants;
- create personal movement histories;
- infer private identity from aircraft data;
- circumvent aviation/security restrictions;
- bypass provider access controls or terms;
- automate accusations against people, operators or institutions;
- publish sensitive operational coordinates merely because they were observable.

Rate limits, retention limits, source allowlists/denylists, redaction, aggregation and human review should be used where appropriate.

## 10. Retention

Raw citizen media is not a Janavani server-side default. If a user voluntarily uploads evidence, retention must be limited to the documented purpose and disclosed before upload. Derived evidence should be minimized and deletable where feasible.

Public telemetry and environmental observations should use purpose-based retention and should not become an unrestricted historical movement database.

## 11. Architecture

The initial implementation must reuse existing Janavani evidence/provenance/repository contracts.

Proposed capabilities:

- Observation Contract
- Evidence Contract
- Provenance Contract
- Atmospheric Event Contract
- Correlation Contract
- Alert Policy Contract
- Citizen Media Intake Contract
- RTI Draft Generation Contract

No new production database or provider should be introduced until the existing repository/provider audit identifies a concrete need.

## 12. Human review

High-impact classifications, public attribution, sensitive-source handling and RTI generation should be reviewable. Automated analysis may identify leads but must not silently convert a hypothesis into a factual claim.

## 13. Acceptance criteria

A compliant implementation:

- is local-first for raw citizen media;
- collects only necessary information;
- never silently uploads camera media;
- never submits an RTI directly;
- exports RTI drafts for user review/submission;
- excludes sensitive government/military aviation information by policy;
- does not infer mission purpose from aircraft pattern alone;
- preserves provenance for retained evidence;
- supports provider replacement and graceful degradation;
- has negative tests for privacy, sensitive-data and attribution failures;
- uses existing Janavani evidence/repository boundaries wherever possible.
