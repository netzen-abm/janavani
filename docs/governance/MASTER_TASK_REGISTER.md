# Janavani Master Task Register

**Canonical baseline:** `main` @ `d5c3ae0336cf1d9fb92c0eca2dd87d475a1ae107`
**Last re-baselined:** 2026-09-22

This is the execution register. Older checklists, roadmaps, issue lists, and branch plans remain historical evidence unless explicitly referenced here.

## P0 — Governance and architecture convergence

- [x] Canonical `main` identified and re-baselined at `c855773`.
- [x] Canonical `main` ruleset specification committed.
- [ ] Configure actual GitHub `main` protection/ruleset in repository Settings.
- [ ] Complete whole-repository boundary audit from the current `main` baseline.
- [ ] Classify every direct provider/repository construction site.
- [ ] Classify every direct storage/database access site.
- [ ] Classify every surface-owned persistence path.
- [ ] Identify and converge duplicate capability owners.
- [ ] Identify remaining legacy bypasses and archive only after evidence.
- [ ] Update Source of Truth and architecture decision records from audit evidence.
- [x] Establish strict nine-branch operating target; no new long-lived branch without explicit architectural purpose.
- [x] Safely retire all non-survivor branches; GitHub branch inventory currently verifies exactly nine active branch refs. Historical work is preserved as archive evidence; no extra active branch refs remain.
- [x] Promote Civic Case Python/Rust lifecycle parity evidence to `main`.

## P0 — Canonical runtime and persistence boundary

- [ ] Finish canonical runtime/deployment authority verification.
- [ ] Verify Docker/Procfile/Compose/deployment manifests agree on one authoritative application target.
- [ ] Verify full Python/Rust/Dioxus test orchestrator on canonical `main` or record exact blockers.
- [ ] Keep PostgreSQL migration blocked until boundary audit and runtime evidence justify it.
- [x] Retire Supabase from the active runtime/build graph; preserve historical evidence under archive/legacy/.
- [ ] Verify all durable repositories are selected only by composition/provider boundaries.

## P0 — Shared civic domain

- [x] Canonical Case domain/lifecycle foundation.
- [x] Shared provider composition boundary.
- [ ] Complete Case → Evidence → Authority → Document → Review vertical slice.
- [ ] Complete Submission → acknowledgement → tracking lifecycle.
- [ ] Converge constitutional objection route into canonical CivicActionCapability.
- [ ] Complete obligation/responsibility integration and verify source/provenance semantics.

## P0 — Privacy, authorization and safety

- [ ] Enforce admin zero-access security contract.
- [ ] Complete capability-scoped consent and authorization enforcement.
- [ ] Verify protected data does not reach logs/telemetry/URLs/metrics/support tooling.
- [ ] Verify AI/Agentic AI receives only authorized/minimized context.
- [ ] Verify consequential agent actions have policy and human approval gates.
- [ ] Audit safety-critical SOS routing before refactor; never replace real delivery with synthetic success.

## P1 — Canonical product surface

- [ ] Select and freeze the first production vertical-slice surface after architecture audit.
- [ ] Build the canonical citizen workspace against shared contracts only.
- [ ] Verify local-first evidence and protected-data handling in the actual target client.
- [ ] Complete document generation/review/download; keep document generation separate from submission.
- [ ] Complete authority discovery with verified source/provenance and ambiguity handling.

## P1 — Access-surface convergence

- [ ] Telegram Bot consumes shared capabilities instead of route-specific storage/business logic.
- [ ] Telegram Mini App consumes shared contracts independently.
- [ ] Android and iOS remain independent consumers of shared contracts.
- [ ] DApp/Web3 remains independent and optional for users.
- [ ] WhatsApp/Messenger adapters consume shared capabilities.
- [ ] Failure of one surface/provider/model does not block unrelated surfaces/capabilities.

## P1 — AI and intelligence infrastructure

- [ ] Canonical AI capability/router boundary.
- [ ] Ollama/local AI adapter behind provider contract.
- [ ] Cloud AI adapters behind same contract.
- [ ] RAG/OCR/CV/VLM/SLM/LLM/Agentic AI treated as replaceable implementations, not surface-owned logic.
- [ ] Deterministic/degraded paths for critical civic workflows.
- [ ] AI provenance and source-grounding rules verified.

## P1 — Evidence and resilience

- [ ] Actual local evidence capture/storage implementation.
- [ ] Hashing/integrity and provenance verification.
- [ ] Metadata/EXIF minimization where applicable.
- [ ] User-controlled recovery/key lifecycle production design.
- [ ] Optional decentralized providers/adapters only behind stable contracts and truthful degraded states.

## P2 — Ecosystem expansion

- [ ] Full Android/iOS product hardening.
- [ ] DApp/Web3 hardening.
- [ ] Offline/low-bandwidth resilience.
- [ ] Mesh/satellite capability adapters where justified and verified.
- [ ] Broader civic action types and authority datasets.
- [ ] Accountability/outcome learning layer.

## P2 — Research / strategic infrastructure

- [ ] Digital Swaraj / technological sovereignty doctrine integration after architecture is stable.
- [ ] External civic-channel learning incorporated as research, not copied product architecture.
- [ ] Hardware/device evidence and trusted-capture research evaluated behind capability contracts.
- [ ] Future technologies evaluated using reuse-first, evidence-first, provider-neutral criteria.

## Branch operating policy — strict nine-branch target

The repository operating target is exactly nine long-lived branches:

1. `main` — canonical convergence line.
2. `integration/canonical-platform` — shared platform integration.
3. `feat/canonical-case-kernel` — canonical Case kernel work.
4. `feat/canonical-capability-execution-envelope` — shared execution-context contract.
5. `feat/canonical-civic-action-vertical-slice` — civic-action vertical slice.
6. `feat/canonical-sos-contract` — SOS contract/decomposition.
7. `feat/capability-scoped-consent-agent-enforcement` — consent/agent security.
8. `audit/postgres-provider-production-gates` — durable-provider readiness.
9. `chore/ecosystem-shared-capability-infrastructure` — shared ecosystem infrastructure.

This is the active survivor target. Existing refs must be compared with `main`; useful deltas are selectively converged, evidence is preserved, and only then are source refs deleted.

### Branch lifecycle

`one focused branch → verify → converge/promote → archive evidence → delete`

Rules:

1. No `-v2`, `-v3`, `-final`, `-clean` branch generations.
2. No new long-lived branch unless it matches an approved role.
3. Never blindly merge a stale branch merely to reduce branch count.
4. Archive-first applies to branch retirement.
5. A branch fully behind `main` is a retirement candidate.
6. A branch whose useful delta is already on `main` is a retirement candidate.
7. Open PRs are not canonical merely because they exist.
8. Current `main` is the convergence authority.
9. Physical deletion must be real deletion; force-moving a ref is not deletion.

`main` currently has historical refs beyond this nine-role target. The repository must not be reported as physically converged until those refs are actually deleted.

## Rules for execution

1. Audit before implementing.
2. One canonical owner per capability/function.
3. Shared infrastructure first; interfaces consume it.
4. Optional means user choice, not ecosystem omission.
5. Archive before delete.
6. Preserve useful work; converge rather than rewrite for naming alone.
7. No PostgreSQL migration merely because PostgreSQL exists; prove the boundary and runtime first.
8. Code + tests + runtime/deployment evidence = completion.
9. Do not create a new abstraction when an existing canonical contract can be strengthened.
10. Every completed item must reference code/test/evidence where applicable.
11. Never report green unless the exact current commit has verified green evidence.


## 2026-09-22 branch hygiene re-verification

GitHub's live branch inventory for `netzen-abm/janavani` was queried directly and returned exactly the nine sanctioned active branch refs. No additional active branch ref remains. The earlier 249-ref retirement baseline is historical evidence and must not be used as the current active-branch count. Responsibility-boundary audits continue independently; branch hygiene is now at the nine-branch target.
