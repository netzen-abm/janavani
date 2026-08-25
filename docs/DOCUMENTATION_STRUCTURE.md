# Janavani Documentation Structure

**Status:** Governing documentation-organization standard  
**Scope:** Repository documentation, planning material, audits, architecture records, operational guides, and historical documentation  
**Rule:** Evaluate → Audit → Compare → Modify/Merge → Archive → Delete only with evidence

## 1. Purpose

Janavani has accumulated documentation across the repository root, `docs/`, `planning/`, application generations, and historical/archive locations. This file defines the target organization so documentation does not become another multi-generational architecture.

The goal is **one discoverable documentation system**, not one giant document.

## 2. Documentation authority hierarchy

Use this order when documents disagree:

1. `docs/SOURCE_OF_TRUTH.md` — ecosystem-level authority.
2. `docs/ECOSYSTEM_CHARTER.md` / `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — ecosystem scope and constitutional intent.
3. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — canonical system architecture.
4. `docs/ARCHITECTURE_PRINCIPLES.md` — architectural engineering rules.
5. `docs/ARCHITECTURE_DECISIONS.md` — accepted ADR record; must reference superseding decisions rather than silently conflict.
6. `docs/CAPABILITY_REGISTRY.md` — capability contracts/status/index.
7. Domain-specific contracts and architecture documents.
8. Execution plans, audits, checklists, and working documents.
9. Historical/archive material — evidence only unless explicitly promoted.

A lower-level document must not silently redefine a higher-level rule.

## 3. Target directory taxonomy

```text
docs/
├── 00-governance/       # constitution, charter, source-of-truth, decision process
├── 10-architecture/     # system architecture, boundaries, runtime/client ownership
├── 20-capabilities/     # capability registry, capability contracts, capability maps
├── 30-domain/           # civic, grievance, RTI, petition, evidence, legal/domain contracts
├── 40-platform/         # shared infrastructure, storage, events, identity, AI platform contracts
├── 50-interfaces/       # web, Android, iOS, DApp, Telegram, WhatsApp, Messenger, future adapters
├── 60-operations/       # deployment, CI/CD, runtime, release, observability, incident procedures
├── 70-security-privacy/ # privacy, security, safety, consent, identity, threat controls
├── 80-development/      # developer guide, contributing, testing, code-quality guidance
├── 90-audits/           # repository, runtime, import, dependency, documentation, migration audits
├── archive/             # preserved historical material; never treated as current authority
└── DOCUMENTATION_STRUCTURE.md
```

The first migration phase may leave source files in their existing locations when moving them would break active references. Such files must be indexed and classified until link/reference migration is verified.

## 4. Classification rules

Every documentation artifact receives one classification:

- **CANONICAL** — current authority for a defined scope.
- **SUPPORTING** — explains or implements a canonical decision without redefining it.
- **EXECUTION** — current plan/checklist/status used to implement the architecture.
- **AUDIT** — evidence about repository/runtime state at a point in time.
- **EXPERIMENTAL** — proposal or prototype that is not an architectural authority.
- **HISTORICAL** — retained evidence from an earlier generation.
- **DUPLICATE / MERGE CANDIDATE** — overlapping content requiring comparison.
- **ORPHANED** — not referenced and not clearly owned; keep until evaluated.

## 5. Known canonical document families

### Governance / authority

- `docs/SOURCE_OF_TRUTH.md`
- `docs/ECOSYSTEM_CHARTER.md`
- `docs/JANAVANI_ECOSYSTEM_CHARTER.md`
- `docs/JANAVANI_CONSTITUTIONAL_GOVERNANCE.md`
- `planning/FOUNDER_CONSTITUTION.md`
- `planning/ENGINEERING_CONSTITUTION.md`
- `planning/ECOSYSTEM_ENGINEERING_CONSTITUTION.md`

These must be compared for authority and overlap before any merge or archive decision.

### Architecture

- `docs/JANAVANI_MASTER_ARCHITECTURE.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_PRINCIPLES.md`
- `docs/ARCHITECTURE_DECISIONS.md`
- `docs/ARCHITECTURE_DATA_BOUNDARY.md`
- `docs/CANONICAL_API_ASSEMBLY_DESIGN_2026-08-23.md`
- `docs/CANONICAL_API_ROUTE_OWNERSHIP_MAP_2026-08-23.md`
- `docs/CANONICAL_RUNTIME_AND_CLIENT_OWNERSHIP_2026-08-24.md`
- `planning/ARCHITECTURE_INDEX.md`

### Capabilities

- `docs/CAPABILITY_REGISTRY.md`
- `docs/CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md`
- `planning/DOCUMENT_CONTRACT.md`
- other capability-specific contracts and maps

### Privacy / safety / security

- `planning/PRIVACY_ARCHITECTURE.md`
- `planning/PRIVACY_CONTRACT.md`
- `docs/PRIVACY_SAFETY_BY_DESIGN.md`
- security-specific contracts in `docs/`

### Data / storage

- `planning/DATABASE_CONTRACT.md`
- `planning/DATABASE_DESIGN.md`
- `planning/DATA_DICTIONARY.md`
- storage ownership maps and data-boundary documents

### Operations / release / audits

- repository/runtime/import/deployment audits;
- release checklists;
- acceptance and verification documents;
- CI and deployment guidance.

### Development

- `README.md`
- `CONTRIBUTING.md`
- `docs/DEVELOPER_GUIDE.md`
- `docs/CODE_QUALITY.md`
- `README-AI-OPS.md`

## 6. Migration protocol

Documentation is migrated in batches, never by blind mass move.

For each candidate:

1. Read the complete document.
2. Identify owner/scope and date.
3. Search repository references to it.
4. Compare against canonical documents.
5. Decide: keep, edit, merge, relocate, archive, or delete.
6. If archiving, copy the exact source to `docs/archive/` first.
7. Update inbound links and indexes.
8. Verify references and navigation.
9. Record the decision in the documentation audit.
10. Only delete after evidence shows the active copy is no longer required.

## 7. Naming rules

Prefer descriptive, stable names over repeated date-stamped generations.

Use dates when a document is specifically a point-in-time audit, snapshot, migration record, or release record.

Examples:

- Good: `CANONICAL_RUNTIME_AND_CLIENT_OWNERSHIP_2026-08-24.md` for a dated audit/snapshot.
- Good: `CAPABILITY_REGISTRY.md` for a living registry.
- Avoid creating `ARCHITECTURE_V2.md`, `ARCHITECTURE_FINAL.md`, `ARCHITECTURE_FINAL2.md`, etc.

## 8. Cross-document rules

Every canonical document should state:

- its scope;
- status;
- owner/responsibility;
- relationship to higher-level authority;
- related contracts;
- whether it is living or point-in-time;
- last substantive review date.

A new implementation must update the relevant documentation in the same change set. A new architecture decision must be recorded once and referenced elsewhere rather than copied into many competing documents.

## 9. Archive policy

`docs/archive/` is evidence storage, not a second active architecture.

Archived material must:

- remain readable;
- retain original content where practical;
- identify why it was archived;
- identify its replacement, if known;
- not be referenced as current architecture unless explicitly marked historical.

No historical file is deleted merely because it is old.

## 10. Current cleanup observation

The repository already contains a useful documentation-convergence audit and a documentation index. Those are inputs to this structure, not documents to ignore. The current cleanup therefore **reconciles existing documentation rather than inventing another architecture generation**.

## 11. Completion criteria

Documentation cleanup is complete only when:

- every active document has a classification and owner;
- canonical authority is unambiguous;
- duplicate/overlapping documents have documented dispositions;
- active links resolve;
- historical documents are separated from active authority;
- root-level entry documents point to the canonical documentation system;
- new code/capabilities have corresponding documentation;
- privacy, safety, security, and independence requirements are represented in the appropriate canonical documents;
- no document claims an implementation is complete without supporting code/test evidence.
