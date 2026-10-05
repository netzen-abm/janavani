# Janavani Programming + Markdown Audit — 2026-10-05

## Scope

Audited the live `main` tree of `netzen-abm/janavani`, including active programming files and active Markdown files, with archived material excluded from active counts.

## Repository inventory

- Total tracked tree entries: 870
- Active/non-archive files: 678
- Active programming/configuration files: 430
  - Python: 399
  - Rust: 16
  - SQL: 6
  - Shell: 8
  - JavaScript: 1
- Active Markdown files: 209
- Active code is therefore still predominantly Python, with Rust concentrated in the canonical-core direction.

## Branch hygiene

Exactly nine active branches are present:

1. `main`
2. `integration/canonical-platform`
3. `feat/canonical-case-kernel`
4. `feat/canonical-capability-execution-envelope`
5. `feat/canonical-civic-action-vertical-slice`
6. `feat/canonical-sos-contract`
7. `feat/capability-scoped-consent-agent-enforcement`
8. `audit/postgres-provider-production-gates`
9. `chore/ecosystem-shared-capability-infrastructure`

**Decision:** no branch mutation is required. The nine-branch invariant is already satisfied. Do not create a tenth long-lived branch. Do not delete one of the nine until its capability evidence has been merged or explicitly retired.

## Architecture assessment

### Strong boundaries already established

- `src/core/` contains cohesive domain/core contracts.
- `src/capabilities/` exposes shared capability façades.
- `src/storage/repositories/` owns persistence/provider mechanics.
- `src/platform/` owns shared composition.
- `src/web/` and channel adapters remain surface boundaries.
- `src/access/` owns authorization, consent, scope and consequential-operation controls.
- `src/ai/` contains the provider-neutral AI contract and gateway.
- Compatibility entry points for `src/web.py` and `src/web/app.py` correctly delegate to the canonical Web assembly rather than creating a second runtime.

These boundaries match the repository rule: split only at independent change, trust, persistence, provider, runtime or reuse boundaries.

### Do not split further mechanically

The following patterns are intentional and should be preserved:

- `core/civic_case.py` is a stable compatibility surface over the cohesive Case model.
- `capabilities/civic_case.py` is a public façade over contract/implementation/lifecycle modules.
- Submission has already been decomposed into façade, flow, state, security and provider boundaries.
- Repository modules separate domain contracts from provider implementations.
- Surface composition is separate from business capability ownership.

Further splitting without a new architectural boundary would increase orchestration duplication and weaken invariants.

## High-value findings

### P0 — AI/provider boundary is not yet closed

1. `src/services/legal_agent.py` correctly uses `AIExecutionGateway` for legal-document generation, but it also performs a direct Hugging Face HTTP request for translation.
2. This creates an alternate AI/provider execution path outside the canonical AI gateway.
3. `src/ai/providers/ollama.py` is provider-shaped but does not currently implement the canonical `AIProvider.generate(AIRequest) -> AIResponse` contract; it exposes a separate async method and therefore cannot be treated as a drop-in canonical provider.
4. OpenRouter is instantiated inside `legal_agent.py`; provider selection should ultimately be composed at the shared platform boundary rather than becoming service-owned policy.

**Required outcome:** every AI/model/translation provider invocation must cross a canonical capability execution/trust boundary. Provider adapters may perform network I/O; they must not become authorization or capability owners.

### P0 — PostgreSQL/runtime evidence still outranks new capability work

The master checklist still has real PostgreSQL authorization/RLS, restart/recovery, backup/restore and runtime-entrypoint verification open. These are production-gate items, not optional cleanup.

### P1 — Active codebase is large but not primarily suffering from file-size problems

The earlier codeline audit already recorded that major submission/provider files were decomposed at responsibility boundaries. The current tree contains many similarly named modules because domain, capability and persistence responsibilities are distinct. This is acceptable where the dependency direction is one-way and ownership is clear.

The correct next audit is therefore **duplicate behavior/import ownership**, not a blanket file split.

### P1 — Legacy/compatibility surfaces require reachability verification

Examples include:

- `src/main.py`
- `src/web.py`
- `src/web/app.py`
- `src/web_mvp/`
- messaging bootstrap modules

Compatibility shims should remain until runtime/deployment references are proven migrated. Archive-first retirement remains mandatory.

### P1 — Documentation volume is now a governance risk

209 active Markdown files exist. The repository has a strong canonical-document hierarchy, but multiple dated audits, plans, status documents and architectural references can create drift.

**Action:** maintain one canonical document per subject; dated audits are evidence, not competing architecture. New Markdown should be created only when it owns a distinct subject or records dated evidence.

## Master priority reset

### P0 — Production convergence gate

1. PostgreSQL real-runtime authorization/RLS evidence.
2. Restart/outage/recovery and backup/restore evidence.
3. Canonical Web/API runtime verification.
4. CI/security/architecture execution evidence.
5. Close every AI/provider invocation path through canonical execution/trust boundaries.
6. Make Ollama conform to the provider contract or explicitly keep it outside the production provider registry until conformance is implemented.

### P1 — Canonical shared infrastructure

7. Capability → repository → tests → deployment → security/privacy map.
8. Storage ownership/concurrency/UoW verification.
9. Canonical execution/provenance envelope adoption across remaining capabilities.
10. Cross-surface Case continuity and capability parity verification.
11. Evidence local-first implementation and authorized transmission flow.

### P2 — Product vertical completion

12. Complete one end-to-end civic-action vertical: understand → jurisdiction → authority → evidence → document → review → approval → citizen-controlled submission → acknowledgement → tracking → follow-up.
13. Expand document, RTI, authority, accountability and knowledge capabilities from the canonical contracts.
14. WebApp completion against the shared capability graph.
15. Telegram migration to complete shared capability parity.

### P3 — Ecosystem expansion

16. Mini App.
17. Android/iOS.
18. WhatsApp/Messenger.
19. SOS/resilient transports.
20. decentralized/Web3 capabilities.
21. broader AI/RAG/OCR/CV/VLM/agentic capabilities.

### P4 — Hardening and scale

22. System-wide threat model.
23. Security/privacy verification.
24. Failure injection and resilience.
25. accessibility/multilingual/low-bandwidth verification.
26. production observability, backup/restore and incident response.
27. real-device and field testing.

## Branch operating rule

Maintain exactly nine active branches. A branch may be merged/retired only after:
- capability scope is identified;
- useful commits are compared with `main`;
- dependencies/imports/tests are checked;
- replacement is proven;
- CI/security evidence is green;
- historical value is preserved;
- the branch is no longer needed as an independent architectural workstream.

## Audit conclusion

**Architecture quality: strong. Repository hygiene: improving and currently branch-compliant. Product implementation: still behind architecture.**

The next engineering work should reduce architectural entropy, not add another abstraction generation.

## Evidence

- `docs/SOURCE_OF_TRUTH.md`
- `docs/REPOSITORY_RULES.md`
- `docs/MASTER_TASK_CHECKLIST.md`
- `docs/90-audits/PROGRAMMING_CODELINE_AUDIT_2026-09-21.md`
- live GitHub tree and branch inventory reviewed 2026-10-05
