# JANAVANI — DOCUMENTATION STRUCTURE

**Status:** ACTIVE — documentation organization standard  
**Version:** 1.0  
**Date:** 11 September 2026  
**Scope:** Entire Janavani repository

## 1. Purpose

This document defines how Janavani documentation is organized so that humans, developers, automated agents and future contributors can identify the correct source without reconstructing decisions from chat history.

The goal is **one documented truth hierarchy, clear ownership, no competing active documents, and preserved historical evidence**.

This is an organization standard. It does not itself change product scope or architectural authority.

## 2. Authority hierarchy

When documents disagree, resolve them in this order:

1. `docs/JANAVANI_NORTH_STAR.md` — strategic destination and civic purpose.
2. `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — locked identity and ecosystem scope.
3. `docs/JANAVANI_CONSTITUTIONAL_GOVERNANCE.md` — constitutional/legal framing and governance constraints.
4. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules and current implementation boundaries.
5. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — detailed architecture.
6. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — ecosystem capability/product landscape.
7. `ROADMAP.md` — construction sequence.
8. `docs/CAPABILITY_REGISTRY.md` and `planning/` contracts — capability and engineering specifications.
9. `docs/MASTER_TASK_CHECKLIST.md` — canonical task inventory.
10. `docs/MASTER_TASK_CHECKLIST_STATUS_*.md` — dated execution/status evidence.
11. `docs/architecture/` — bounded architecture contracts, decisions and implementation-boundary records.
12. `docs/90-audits/` — dated audits and verification evidence.
13. `implementation + tests + CI + deployment evidence` — what is actually verified in the repository/runtime.
14. `archive/` and historical generation trees — preserved evidence only; never current authority unless explicitly promoted.

A lower-level document must not silently override a higher-level document. If a lower-level implementation requires a deliberate architectural change, record an ADR and update the relevant canonical document.

## 3. Directory responsibilities

### Root

Keep only project entry points, top-level operational documentation and configuration that developers reasonably need immediately.

Examples: `README.md`, `README-AI-OPS.md`, `ROADMAP.md`.

### `docs/`

Current project documentation and canonical cross-cutting references.

Use stable names for current authorities and dated names for point-in-time evidence.

### `docs/architecture/`

Current architectural contracts, decision records, bounded implementation-boundary documents and architecture-specific design/verification records.

A document here should answer one architectural question or define one bounded contract. Avoid creating a second document merely to restate an existing contract.

### `docs/90-audits/`

Dated audits, reconciliation records, cleanup registers, verification reports and evidence snapshots. These are historical evidence of what was observed at a particular point in time, not permanent architectural authority.

### `planning/`

Active engineering specifications, product requirements and detailed contracts that support the canonical architecture. Planning documents must link upward to their governing canonical documents.

### `archive/`

Historical, superseded or deprecated material retained for traceability. Archived documents must state why they were archived and what replaced them, where known.

### `janavani_v2/` / `janavani_v3/`

Historical or parallel generation trees. Their documentation is not current authority unless explicitly referenced by current canonical documentation and verified against the current implementation.

## 4. Naming rules

Use:

- `CANONICAL_NAME.md` for a stable current contract or authority.
- `DESCRIPTIVE_NAME.md` for a current supporting document.
- `NAME_YYYY-MM-DD.md` for a dated audit/status/evidence record.
- `ADR-NNN-SHORT-NAME.md` for a dedicated ADR when a decision deserves its own document.
- `archive/...` for superseded material.

Avoid spaces, emojis, generation suffixes and ambiguous names in active documentation paths.

Do not create `*_FINAL`, `*_FINAL2`, `*_NEW`, `*_LATEST`, `*_V2` or similar competing active documents. Version the content inside the canonical document or create a dated evidence record when a snapshot is genuinely required.

## 5. Document status vocabulary

Use one primary status:

`CANONICAL / LOCKED / ACTIVE / IN PROGRESS / VERIFYING / DESIGN COMPLETE / EVIDENCE / HISTORICAL / SUPERSEDED / ARCHIVED`

`COMPLETE` is reserved for implementation claims that satisfy the repository's completion evidence standard; documentation existence alone never makes a capability complete.

## 6. Required header for active technical documents

Where practical, active technical documents should identify:

- Status
- Date or last verified date
- Scope
- Authority/parent document
- Implementation paths when applicable
- Verification/evidence paths when applicable

This lets both human and AI contributors quickly determine whether a document is current, normative, historical or merely descriptive.

## 7. Non-duplication protocol

Before creating or substantially changing documentation:

1. Read this structure standard.
2. Read the authority hierarchy.
3. Search existing `.md` files for the subject, filename and referenced terms.
4. Compare the closest existing documents before drafting.
5. Identify whether the need is a correction, update, merge, rename, archive or genuinely new document.
6. Preserve historical evidence; do not rewrite dated records to hide past state.
7. Update inbound references when moving or renaming a file.
8. Record the disposition in the documentation cleanup register.

## 8. Documentation versus implementation truth

Documentation describes intent, contracts or observed evidence. Code and tests establish implementation facts. CI/deployment/runtime evidence establishes operational facts.

Never convert:

- design → implementation;
- code existence → functional completion;
- CI green → production readiness;
- an AI/model result → authoritative fact;
- a transport response → government acknowledgement.

## 9. Current architecture-control-plane documentation

The following documents form one non-duplicative control-plane family:

- `docs/architecture/CAPABILITY_EXECUTION_ENVELOPE.md` — operation/execution context contract.
- `docs/architecture/CANONICAL_AUTHORIZATION_KERNEL.md` — authorization boundary.
- `docs/architecture/EXECUTION_AWARE_CONSENT.md` — execution-identity binding for consent.
- `docs/architecture/CONSEQUENTIAL_OPERATION_GATE.md` — composition boundary for consequential operations.
- `docs/architecture/CANONICAL_CIVIC_ACTION_SPINE.md` — civic-action capability composition.
- `docs/architecture/SUBMISSION_DELIVERY_CONVERGENCE_2026-09-09.md` — dated submission/delivery evidence.

Their responsibilities are intentionally separate:

```text
Identity
  ↓
Authorization / Policy Decision
  ↓
Consent (when required)
  ↓
Explicit Approval (when required)
  ↓
Execution Context / Operation Trace
  ↓
Capability
  ↓
External Side Effect
```

The common gate composes these controls; it does not replace their individual authorities.

## 10. Current civic-action architecture

The canonical civic-action composition is:

```text
Observation / Citizen Reality
        ↓
Evidence + Provenance
        ↓
Authority / Jurisdiction Resolution
        ↓
Case
        ↓
Document Draft
        ↓
Review + Correction
        ↓
Explicit User Approval
        ↓
Consequential Operation Gate
        ↓
Submission / Delivery
        ↓
Independent Acknowledgement Evidence
        ↓
Government Outcome
        ↓
Citizen Verification
        ↓
Reopen / Follow-up / Escalation
```

Responsibility resolution may progressively identify asset, jurisdiction, authority, department, office, project, contract, contractor/vendor, responsible role, obligation and remedy. AI may assist with discovery and analysis, but must not manufacture responsibility or become the final authority for guilt, liability, corruption, misconduct or legal determination.

## 11. Documentation disposition rules

### Keep active

Keep documents that define a unique current authority, contract, capability, decision, requirement or necessary navigation function.

### Update in place

Use when the document remains the correct authority but its implementation state, links, terminology or evidence has changed.

### Rename/move

Use when the content is still valid but its path or name violates the current structure. Preserve content and migrate inbound links in the same convergence change.

### Archive

Use when a document is superseded, generation-specific, obsolete or a historical snapshot. Archive first and state the reason/replacement.

### Delete

Only after archive, reference, dependency, historical-value and replacement checks establish that deletion is safe. Never delete merely because a document is old.

## 12. Immediate cleanup policy

This organization pass therefore does **not** perform blind mass renames or deletions. Existing documentation is first classified by authority, scope, overlap, implementation relevance and historical value. High-confidence contradictions/duplicates are corrected in bounded changes; uncertain material remains preserved until evidence supports a disposition.

## 13. For AI agents and developers

Before making repository changes:

```text
Read authority → locate current contract → inspect implementation → inspect tests
→ identify unresolved delta → make bounded change → verify → update evidence
→ update affected docs → never invent missing evidence
```

If two documents appear to compete, do not choose based on filename or recency alone. Follow the authority hierarchy and inspect the repository evidence.

**Rule:** The repository must remain understandable without access to the original chat conversation.
