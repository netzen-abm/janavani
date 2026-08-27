# Janavani — Living Execution Task Tracker

**Last updated:** 27 August 2026  
**Purpose:** Single working checklist for the current repository-convergence + ecosystem-build program.

> This tracker supersedes scattered conversational task lists. It is intentionally execution-oriented. A checkbox is marked complete only when repository evidence, tests and/or runtime verification support it.

## A. Strategy and product direction

- [x] Establish Digital Swaraj as the strategic doctrine above product roadmaps.
- [x] Define Janavani as a Civic Action Operating System / ecosystem rather than a single-channel app.
- [x] Define the **Civic Action Workspace** as the first product wedge.
- [x] Define **Case** as the durable atomic unit of citizen civic work.
- [x] Define the first complete lifecycle: issue → understanding → authority → evidence → action/document → review → approval → submission → tracking → follow-up → outcome.
- [x] Define Web/WebApp as the first product-building surface.
- [x] Define interface independence for Web, Telegram, Mini App, Android, iOS, WhatsApp, Messenger, DApp and future clients.
- [x] Define progressive decentralization instead of making blockchain/decentralized infrastructure an immediate product dependency.
- [x] Add Digital Swaraj/product/case-capability documentation to the repository strategy branch.

## B. Repository convergence / hygiene

- [x] Establish active-runtime vs archive/legacy CI boundary.
- [x] Preserve historical code rather than deleting it merely to satisfy CI.
- [x] Scope active Python CI validation to the current runtime/test boundary.
- [x] Fix canonical complaint repository test import namespace.
- [x] Fix malformed delivery profile implementation.
- [x] Fix land-router typing/import defect found by CI.
- [x] Fix legal-agent anti-open-chat contract failure.
- [ ] Trace remaining active references to legacy document generators.
- [ ] Produce Capability → Repository → Test → Deployment ownership map.
- [ ] Verify storage ownership and remove/converge duplicate active storage paths.
- [ ] Identify duplicate/superseded runtime entry points.
- [ ] Archive superseded active candidates only after dependency tracing.
- [ ] Update project map / README / roadmap where convergence changes the canonical path.

## C. CI / verification

- [x] Python syntax/compile validation reached the active `src/` tree.
- [x] Canonical Python suite reached 62/62 passing in the latest verified run before the Dioxus changes.
- [x] Startup/import check passed on the Web build repair cycle.
- [ ] Verify latest Dioxus/Web build after browser API and event-handler fixes.
- [ ] Add/maintain active Web build verification in CI.
- [ ] Add degraded-path tests for optional AI/provider failures.
- [ ] Add contract tests for Case lifecycle transitions.
- [ ] Add integration test for first complete civic-action vertical slice.
- [ ] Establish release-gate evidence: tests + security + privacy + runtime + deployment.

## D. Shared domain / Case kernel

- [x] Create initial channel-neutral `Case` domain model.
- [x] Define explicit Case lifecycle states.
- [x] Add append-only Case domain event representation.
- [x] Add initial Case transition tests.
- [ ] Reconcile Case model with existing `docs/DATA_CONTRACTS.md`.
- [ ] Reconcile Case model with existing capability registry.
- [ ] Define stable Case identifier/version semantics.
- [ ] Define Case persistence repository contract.
- [ ] Define authorization boundary around Case access/mutation.
- [ ] Define Case export/import semantics for portability.

## E. Evidence capability

- [ ] Define canonical Evidence object.
- [ ] Separate citizen-provided evidence from generated interpretation.
- [ ] Add provenance/source references.
- [ ] Define evidence verification/correction state.
- [ ] Define privacy/retention metadata.
- [ ] Add Evidence repository contract.
- [ ] Add tests for malformed, missing and duplicate evidence.
- [ ] Integrate Evidence with Case.

## F. Authority intelligence

- [ ] Define canonical Authority/Office object.
- [ ] Converge existing office/directory services behind the authority capability.
- [ ] Establish authoritative source + freshness metadata.
- [ ] Prevent AI-generated/fabricated official recipient data.
- [ ] Support citizen review/correction/selection of authority.
- [ ] Integrate selected authority into Case.
- [ ] Add failure/degraded behavior when directory/search is unavailable.

## G. Document capability

- [x] Establish provider-neutral document renderer boundary.
- [x] Add PDF/DOCX renderer contract tests.
- [x] Route Telegram generation through shared document capability.
- [ ] Trace and converge remaining legacy document generators.
- [ ] Define document versioning against Case revisions.
- [ ] Connect document provenance to evidence and authority data.
- [ ] Expose document review/approval state.

## H. Consent / identity / permissions

- [ ] Define optional Janavani identity model.
- [ ] Define channel authentication boundaries.
- [ ] Define cross-channel identity linking.
- [ ] Define consent records and revocation.
- [ ] Define citizen/expert/volunteer/institution roles.
- [ ] Define least-privilege authorization model.
- [ ] Add access audit events.

## I. Submission / delivery / tracking

- [ ] Define submission capability contract.
- [ ] Define truthful delivery states: not submitted, ready, attempted, delivered, acknowledged, failed, unknown.
- [ ] Capture external acknowledgement/reference where available.
- [ ] Add tracking timeline to Case.
- [ ] Define follow-up actions.
- [ ] Define evidence-supported escalation.
- [ ] Test provider failure without false-success state.

## J. AI / intelligence fabric

- [x] Keep AI behind replaceable provider-neutral boundaries.
- [x] Preserve deterministic/manual fallback when AI is unavailable.
- [x] Establish bounded civic-document AI prompt boundary.
- [ ] Define AI routing policy by capability, sensitivity, user preference and availability.
- [ ] Define source-grounded RAG contract.
- [ ] Define citation/provenance requirements for generated claims.
- [ ] Define agentic-action approval gates.
- [ ] Define evaluation suite for factuality, routing, translation and document quality.
- [ ] Add local/cloud model portability tests.

## K. Web / WebApp — first product surface

- [x] Establish Dioxus Web project and capability-oriented UI direction.
- [x] Repair browser dependency declarations.
- [x] Repair current Dioxus launch/event-handler compatibility issues found by CI.
- [ ] Verify clean Web build in CI.
- [ ] Replace prototype response model with canonical Case/capability API path.
- [ ] Implement Create Case.
- [ ] Implement Understand/clarification flow.
- [ ] Implement Authority selection with provenance.
- [ ] Implement Evidence collection.
- [ ] Implement Document composition/review.
- [ ] Implement explicit approval.
- [ ] Implement submission and truthful delivery state.
- [ ] Implement Case timeline/tracking.
- [ ] Implement follow-up.
- [ ] Add accessibility and multilingual foundations.
- [ ] Add privacy/consent UX.

## L. Telegram Bot + Mini App

- [x] Establish Telegram as an access layer rather than platform core.
- [x] Route document generation toward shared capability boundary.
- [ ] Verify Telegram Bot consumes canonical Case/capability contracts.
- [ ] Remove remaining Telegram-specific business logic duplicates.
- [ ] Implement Mini App against the same backend/capabilities.
- [ ] Ensure Bot and Mini App can operate independently.
- [ ] Share Case state between Web/Telegram only through canonical identity/linking rules.

## M. Mobile / other interfaces

- [ ] Android reference client consuming shared contracts.
- [ ] iOS reference client consuming shared contracts.
- [ ] WhatsApp adapter.
- [ ] Messenger adapter.
- [ ] DApp adapter/client.
- [ ] Voice/accessibility interfaces where justified by user evidence.

## N. Sovereign / resilient infrastructure

- [ ] Provider-neutral storage implementation map.
- [ ] Portable encrypted data/export.
- [ ] Local/edge capability support where justified.
- [ ] Cryptographic provenance/tamper-evident events where justified.
- [ ] P2P/decentralized storage adapter where justified.
- [ ] Alternative transport adapters.
- [ ] Community relay/mesh architecture.
- [ ] Community-operated infrastructure model.

## O. Security / privacy / governance

- [ ] Threat model for Case/evidence/document/submission lifecycle.
- [ ] Privacy threat model and data-minimisation review.
- [ ] Secrets/configuration audit.
- [ ] Authorization tests.
- [ ] Abuse/rate-limit controls.
- [ ] Audit-log integrity review.
- [ ] Incident/recovery procedures.
- [ ] AI safety/red-team evaluation.
- [ ] Production security gate before public launch.

## P. First product release gate

The first complete Civic Action Workspace is **not complete** until a test user can:

- [ ] create a Case;
- [ ] describe a civic problem;
- [ ] answer necessary clarifying questions;
- [ ] select an authority using source-backed information;
- [ ] attach evidence;
- [ ] generate/compose a civic document;
- [ ] review and edit it;
- [ ] explicitly approve it;
- [ ] submit through a supported mechanism;
- [ ] receive a truthful delivery state;
- [ ] see the Case timeline;
- [ ] prepare a follow-up.

And automated verification covers normal, invalid, unauthorized, unavailable-provider and degraded paths.

## Q. Execution rule

For every task, record:

1. **Decision** — what we chose and why.
2. **Repository change** — branch, files and commit.
3. **Verification** — tests/CI/runtime evidence.
4. **Documentation** — affected canonical `.md` document.
5. **Next dependency** — what becomes unblocked.

No task is considered complete solely because code or documentation exists.

## Current focus

**Primary:** Case → Evidence → Authority → Document → Submission → Tracking → Web vertical slice.

**Parallel:** repository cleanup, CI verification, storage ownership mapping, and documentation convergence.

**Deferred:** large-scale mobile expansion, blockchain/token systems, nationwide mesh, custom foundation models and other ecosystem-scale infrastructure until the first civic-action lifecycle is demonstrably useful and stable.
