# Janavani Master Task Register

**Canonical baseline:** `main` @ `baeb042fa9d4d987120367bb5b43eb9e52fec8f8`
**Last re-baselined:** 2026-09-16

This is the execution register. Older checklists, roadmaps, issue lists, and branch plans remain historical evidence unless explicitly referenced here.

## P0 — Governance and architecture convergence

- [x] Canonical `main` identified at `baeb042`.
- [x] Canonical `main` ruleset specification committed.
- [ ] Configure actual GitHub `main` protection/ruleset in repository Settings.
- [ ] Complete whole-repository boundary audit from `baeb042` (Issue #172).
- [ ] Classify every direct provider/repository construction site.
- [ ] Classify every direct storage/database access site.
- [ ] Classify every surface-owned persistence path.
- [ ] Identify and converge duplicate capability owners.
- [ ] Identify remaining legacy bypasses and archive only after evidence.
- [ ] Update Source of Truth and architecture decision records from audit evidence.

## P0 — Canonical runtime and persistence boundary

- [ ] Finish canonical runtime/deployment authority verification (M3-B / Issue #19).
- [ ] Verify Docker/Procfile/Compose/deployment manifests agree on one authoritative application target.
- [ ] Verify full Python/Rust/Dioxus test orchestrator on canonical `main` or record exact blockers.
- [ ] Keep PostgreSQL migration blocked until boundary audit and runtime evidence justify it.
- [ ] Keep Supabase as an adapter; do not treat it as transaction authority without verified atomicity.
- [ ] Verify all durable repositories are selected only by composition/provider boundaries.

## P0 — Shared civic domain

- [x] Canonical Case domain/lifecycle foundation.
- [x] Shared provider composition boundary.
- [ ] Complete Case → Evidence → Authority → Document → Review vertical slice.
- [ ] Complete Submission → acknowledgement → tracking lifecycle.
- [ ] Converge constitutional objection route into canonical CivicActionCapability (Issue #93).
- [ ] Complete obligation/responsibility integration and verify source/provenance semantics.

## P0 — Privacy, authorization and safety

- [ ] Enforce admin zero-access security contract (Issue #24).
- [ ] Complete capability-scoped consent and authorization enforcement.
- [ ] Verify protected data does not reach logs/telemetry/URLs/metrics/support tooling.
- [ ] Verify AI/Agentic AI receives only authorized/minimized context.
- [ ] Verify consequential agent actions have policy and human approval gates.
- [ ] Audit safety-critical SOS routing before refactor (Issue #34); never replace real delivery with synthetic success.

## P1 — Canonical product surface

- [ ] Select and freeze the first production vertical-slice surface after architecture audit (Dynamic Web/WebApp or App/DApp priority must be resolved against current evidence, not historical plans).
- [ ] Build the canonical citizen workspace against shared contracts only.
- [ ] Verify local-first evidence and protected-data handling in the actual target client.
- [ ] Complete document generation/review/download; keep document generation separate from submission.
- [ ] Complete authority discovery with verified source/provenance and ambiguity handling.

## P1 — Access-surface convergence

- [ ] Telegram Bot consumes shared capabilities instead of route-specific storage/business logic.
- [ ] Telegram Mini App consumes shared contracts independently.
- [ ] Android and iOS remain independent consumers of shared contracts (Issue #23).
- [ ] DApp/Web3 remains independent and optional for users (Issue #23).
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
- [ ] Optional decentralized providers/adapters (Freenet/Nostr/IPFS/etc.) only behind stable contracts and truthful degraded states.

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
