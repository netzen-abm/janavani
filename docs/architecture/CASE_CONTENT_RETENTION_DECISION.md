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


## 10. Main-branch content-flow audit — 19 November 2026

This is a read-only source review of the inspected `main` branch. It supplements the policy decision; it does not establish runtime behaviour in a deployed environment.

### WebApp/API path

- `src/web/civic_case_router.py` accepts citizen subject, narrative, claims and jurisdiction in the create request and calls `CivicCaseCapability.create()`.
- `CivicCaseCapability.create()` first saves the metadata aggregate, then writes the citizen content to the injected content repository. In the inspected shared surface composition, that repository defaults to `InMemoryCaseContentRepository`.
- The HTTP create response returns only `case_id` and `status`; it does not return the content for client-side persistence.
- `src/webapp/services/api_client.py` sends the narrative in the HTTPS request but the inspected client exposes no local/IndexedDB content repository or client-side recovery contract.
- `GET /civic/cases/{case_id}` serializes the result of `get_owned()`, which rehydrates content from the process-local adapter when it is present. Therefore, the current path is transient server-side content handling, not device-first storage. Process restart, worker changes or routing to another process can make content unavailable.
- The review/ready endpoints accept subject and narrative again and call `hydrate_transient_content()`, which writes into the same process-local adapter. This is a re-supply mechanism, not proof of device-local persistence.

### Telegram path

- `src/commands/shared_case_capability.py` creates a metadata-only Case shell; the raw narrative is not passed to `create()` and is not written to the Case metadata record.
- The narrative is held in the Telegram conversation/session flow as ephemeral content and re-supplied to the document-generation path. Existing tests assert hydration and subsequent clearing around generation.
- This is transport/session-transient handling, not durable device-local storage. Exact session backend, TTL, persistence, logging and provider behaviour must be verified separately in runtime configuration.

### Document and artifact path

- `src/documents/artifact_service.py` contains `render_artifact_payload()`, which renders to a temporary directory and returns bytes without using the artifact blob store or document artifact repository. This is the preferred ephemeral WebApp download path.
- The same module also contains `generate_artifact()`, which writes rendered bytes to an artifact blob store and returns a persistent reference. Every route and runtime composition must be traced to ensure the non-durable flow cannot silently use this persistent path for citizen narrative without an approved purpose and retention disclosure.
- `DocumentDraft` contains subject and body fields; these are citizen-content-bearing values. Any durable DocumentReview or artifact repository use must be checked for content retention, not assumed safe because the Case table itself is redacted.

### Logging, telemetry and external-provider boundary

The bounded search and inspected files in this pass did not establish that narrative values are logged or sent to analytics/LLM providers, but did not prove their absence across the entire repository or deployed infrastructure. Treat this as **NOT VERIFIED**, not as a clean bill of health. Complete a repository-wide sink review for application logs, request/error middleware, tracing, analytics, crash reports, prompt/provider calls, object storage, database child tables, backups and support tooling.

### Required implementation corrections before claiming device-first

1. WebApp must retain the citizen's working narrative locally (prefer an explicit IndexedDB adapter with owner/session partitioning, versioning and clear lifecycle controls) before submitting it transiently to the API.
2. WebApp Case creation must use a metadata-shell path or otherwise prove that no default durable content write occurs; current `create()` writes into a server process-local adapter and is not an acceptable device-first contract.
3. Return only opaque Case metadata from create; client retains and re-supplies content for authorised actions. Do not serialize transient narrative from a process-local repository as if it were durable Case content.
4. Verify logout/account switch, shared-device isolation, local-data clearing, browser storage denial/quota failure and explicit export/recovery warnings.
5. Telegram must disclose that its content is held in the Telegram interaction/session workflow and can expire; do not represent Telegram session state as citizen-controlled device storage.
6. Trace every document draft/review/artifact route to establish whether content is ephemeral or stored. Disable or gate persistent artifact/review paths until their content retention contract is explicit.
7. Add redaction tests for logs, traces, telemetry and provider payloads; inspect middleware and deployed observability configuration, not only direct logger calls.
8. Test multi-worker/process-restart behaviour: a metadata Case must remain valid while narrative availability is honestly reported as local/transient. No API may imply recovery that the storage layer cannot provide.

### Updated evidence status

- Device-first policy: approved.
- WebApp device-local implementation: not evidenced in inspected main.
- WebApp current handling: transient server-side in-memory repository, with narrative sent in API requests.
- Telegram handling: metadata shell plus transient conversation content; runtime TTL/storage verification pending.
- Ephemeral artifact rendering: implementation path present; route-level exclusive use not fully verified.
- Persistent artifact/document-review retention: route/provider mapping pending.
- Repository-wide log/telemetry/provider leakage audit: not verified.
- Production assurance: not established.

**Decision:** Keep Issue #212 open. Do not claim JANAVANI is already device-first. Implement the client-local WebApp boundary and explicit Telegram expiry disclosure before reconsidering production readiness.
