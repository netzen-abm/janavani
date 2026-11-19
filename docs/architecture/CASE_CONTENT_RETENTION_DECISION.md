# ADR: Civic Case Content Retention and Recovery

- **Status:** DECIDED — POLICY / DESIGN; IMPLEMENTATION PENDING
- **Decision date:** 19 November 2026
- **Scope:** Canonical Civic Case capability and every access surface
- **Related:** GitHub Issue #212; PR #226
- **Decision owner:** JANAVANI product/architecture governance

## 1. Decision

JANAVANI adopts **device-first citizen-content handling as the default**. Citizen-authored Case content (including subject text, narrative, claims and detailed jurisdictional context) must not be silently or automatically retained in JANAVANI server-side durable storage.

A second mode, **explicitly authorised durable retention**, may be offered only where the citizen affirmatively opts in for a clearly stated recovery purpose, defined retention period and disclosed processing/access conditions.

This decision resolves the policy gate in Issue #212. It does not mean either mode is already fully implemented or production-assured.

## 2. Data classification

### 2.1 Minimal Case metadata

The canonical Case record may retain only the fields required for lifecycle, ownership, routing and accountability, subject to the approved data contract and applicable law. The Case metadata record must not contain the citizen's narrative or detailed personal account.

An opaque content reference may be stored only for a separately authorised durable-retention record. The reference must not encode personal information.

### 2.2 Citizen-authored content

Treat the following as citizen content unless a field-specific review establishes otherwise:

- original subject and narrative;
- claims, chronology and supporting explanations;
- detailed location/jurisdiction facts that may identify a person or household;
- attachments and extracted text;
- drafts and generated documents that reproduce citizen content.

Content must remain logically and physically separate from Case lifecycle metadata.

## 3. Tier A — Device-first default

1. The citizen's content remains under the citizen's device/session control; the platform must not create a durable server-side narrative copy by default.
2. Where server processing is required to perform a requested action, process only what is necessary for that action and do not persist the content beyond the explicitly disclosed operational window.
3. Application, proxy, analytics, error and observability logs must not capture narrative bodies, attachments, authentication secrets or generated document contents.
4. No content may be sent to an external AI, analytics, translation or document provider unless the relevant data flow is disclosed and separately authorised where required.
5. The interface must clearly explain that device-first content may not be recoverable on another device or after local browser/app data is cleared, device loss or session expiry.
6. A local draft/vault implementation is a separate engineering deliverable. Do not claim that ordinary browser storage is encrypted or secure by default. Select platform secure storage where available; for web, threat-model key management, XSS exposure, shared-device access and recovery before claiming encrypted local-vault assurance.
7. Provide user-controlled export where feasible. Do not create a hidden server backup as a workaround.

## 4. Tier B — Explicitly authorised durable retention

Durable server-side Case-content retention is permitted only after an affirmative, purpose-specific opt-in. The consent flow must state, before the choice is made:

- what exact content categories will be retained;
- the defined purpose (for example, cross-device access and post-restart recovery);
- the retention period and deletion trigger;
- which JANAVANI operators and service providers can access/process the content;
- whether any external processor or AI provider is involved;
- how the citizen can export, withdraw consent and request deletion;
- any limits on deletion imposed by a clearly identified legal obligation.

Do not bundle this optional retention choice with acceptance of general platform terms or make it a precondition for unrelated capabilities. Record the consent version, purpose, timestamp, principal, scope and withdrawal state. A withdrawal must stop future optional retention and trigger deletion under the documented schedule, subject to any specific lawful retention obligation.

### Required technical controls

- Store content in a separate content domain/table or object store, not in Case narrative columns.
- Encrypt content using an envelope-encryption design; keep key material outside the content database and document rotation, revocation and recovery.
- Enforce principal/owner isolation in the application and database. Test with a non-owner, non-superuser, non-BYPASSRLS runtime role where PostgreSQL RLS is used.
- Keep access and consent audit events free of narrative payloads.
- Enforce retention expiry and deletion, including replicas, caches, derived artifacts and backups according to the documented backup lifecycle.
- Use opaque identifiers and avoid content in URLs, telemetry, exception messages or metrics.
- Do not assume that a database-level RLS policy alone provides complete application security.

## 5. Transaction and lifecycle invariants

Where Tier B is enabled, the Case metadata reference, content record and consent/retention state must be consistent.

- Create/update/delete operations must use one transaction boundary when the stores share PostgreSQL.
- If content is stored in a separate object store, use a documented staged-write/outbox or compensation protocol; do not claim a single ACID transaction across independent systems.
- Failed content writes must not leave a Case pointing to missing content.
- Retries must be idempotent.
- Deletion and consent withdrawal must cover content, references, derived copies and scheduled expiry.
- Restore procedures must preserve consent/retention state and must not resurrect content whose deletion has become effective.

## 6. Shared capability and independent surfaces

WebApp, Telegram and future Android/iOS/other surfaces must call the same canonical Case/content capability contract. Surface adapters must not implement their own retention rules, maintain divergent narrative copies or bypass consent checks.

A citizen may use the device-first mode on one surface and choose the durable-retention mode only through an explicit consent flow. The choice and its scope must be available consistently to all authorised surfaces.

## 7. Acceptance gates for Issue #212

Issue #212 may be closed only after evidence demonstrates:

1. Device-first mode creates no durable server-side citizen-content record by default.
2. Logs, analytics, telemetry and external-provider calls do not silently retain or disclose content.
3. The interface explains local-data loss and recovery limitations accurately.
4. Durable retention is unavailable until explicit, purpose-specific consent is recorded.
5. The consent record is versioned, scoped, auditable and withdrawable.
6. An authorised owner can retrieve retained content after an independent process restart.
7. A different principal is denied access.
8. Metadata/content/consent state remains consistent on failure, retry, update, withdrawal and deletion.
9. PostgreSQL tests use a least-privilege runtime role and verify actual RLS/ownership behaviour.
10. Backup/restore, retention expiry, deletion and key-rotation procedures are tested.
11. WebApp and Telegram use the same canonical capability and demonstrate independent failure/recovery.
12. A privacy/security review approves the actual data-flow and threat model.

Mocks and in-memory repository tests alone do not satisfy these gates.

## 8. Explicit non-decisions

This ADR does not select a specific local-vault library, object store, KMS, cloud provider or encryption algorithm profile. Those choices require a threat model and implementation review. It does not authorise automatic server-side retention, change the existing Case metadata schema, add a migration, or assert production readiness.

## 9. Implementation sequence

1. Map every current content read/write, generated artifact, log and external-provider path.
2. Define the provider-neutral retention/consent contract and local-draft UX.
3. Make device-first the enforced default and prove no durable content writes occur.
4. Implement Tier B only after consent-state and key-management review.
5. Add atomic persistence or a documented cross-store consistency protocol.
6. Prove owner isolation, restart recovery, withdrawal, deletion, backup/restore and cross-surface behaviour using integration tests.
7. Obtain independent privacy/security review before production enablement.

**Governing principle:** JANAVANI must not retain citizen information merely because it can. Retention requires a defined purpose, explicit choice, bounded duration, enforceable access controls and demonstrable deletion.
