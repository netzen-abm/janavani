# JANAVANI — DOCUMENTATION INDEX & AUTHORITY MAP

**Status:** LOCKED — DOCUMENTATION ORGANISATION STANDARD
**Date:** 23 August 2026

This index exists to prevent contradictory documents, duplicate audits and accidental use of historical material.

## 1. Current authority hierarchy

When documents conflict, use this order:

1. `docs/JANAVANI_NORTH_STAR.md` — strategic destination and civic purpose
2. `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — locked identity and ecosystem scope
3. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules
4. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — detailed system architecture
5. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — capability/product landscape
6. `ROADMAP.md` — construction sequence and workstreams
7. `docs/CAPABILITY_REGISTRY.md` + `planning/` contracts — capability/data/engineering specifications
8. `docs/MASTER_TASK_CHECKLIST.md` — master tasks and subtasks
9. `docs/MASTER_TASK_CHECKLIST_STATUS_2026-08-23.md` — current status/evidence register
10. Implementation, tests, CI and deployment evidence — what is actually verified

A dated audit is evidence of what was observed at a point in time. It does not override a current canonical document unless explicitly adopted.

## 2. Directory responsibilities

### Root

Only project-level entry documents and operational configuration should remain here. Historical design notes must not compete with canonical architecture.

### `docs/`

Current architecture, product, governance, audit, deployment, security and evidence documentation.

### `planning/`

Active engineering contracts and detailed specifications that support the canonical architecture.

### `archive/`

Historical, superseded or deprecated documentation retained for traceability. Archived documents are not current instructions.

### `janavani_v2/` and `janavani_v3/`

Historical/parallel implementation trees. Their documentation must not be interpreted as current canonical architecture without evidence from the master checklist and runtime verification.

## 3. Naming standard

- Canonical documents: stable descriptive names.
- Dated audits/status records: `NAME_YYYY-MM-DD.md`.
- Historical documents: move under `archive/` and label them ARCHIVED/SUPERSEDED.
- Avoid duplicate documents whose only difference is wording or date unless the date records a meaningful audit snapshot.

## 4. Document status vocabulary

Use one of:

`CANONICAL / ACTIVE / LOCKED / IN PROGRESS / DESIGN COMPLETE / VERIFYING / EVIDENCE / HISTORICAL / SUPERSEDED / ARCHIVED`

Do not use phrases such as “fully implemented”, “production ready”, or “complete” merely because a file exists.

## 5. Audit non-duplication rule

Before beginning an audit:

1. Read this index.
2. Read the master checklist.
3. Read the latest status register.
4. Read the relevant dated audits.
5. Identify the unresolved delta.
6. Audit only that delta.
7. Record new evidence and update the checklist.

## 6. MVP terminology rule

“MVP” is not a current Janavani product boundary. Historical MVP documents may remain in `archive/` for traceability. Current documentation must describe Janavani as the full ecosystem.

An incremental implementation milestone may be called a milestone, phase, construction unit, pilot, or verified capability — never a product boundary that reduces ecosystem scope.

## 7. Technology language rule

Web, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, API, DApp/Web3, AI, decentralized storage, mesh, Reticulum, Nym, satellite-capable transport and similar technologies are capabilities/interfaces/tools. Their presence in documentation or code does not by itself establish functional completion.

## 8. Source-of-truth rule

If a document disagrees with the actual repository implementation, record the discrepancy. Do not silently rewrite historical evidence to make it appear correct.

The current direction and the actual implementation state are separate facts and must remain distinguishable.

## 9. Cleanup rule

Documentation cleanup may:

- consolidate duplicates;
- correct obsolete terminology;
- move superseded documents to `archive/`;
- update links and authority references;
- create missing indexes;
- clarify ownership and status.

It must not delete historical evidence merely because it is outdated.

## 10. Current documentation cleanup baseline

As of 23 August 2026, the following root-level historical notes were moved to `archive/documentation/legacy/` because they contained obsolete architecture or MVP-era framing:

- `Complete Platform Architecture Index.md`
- `Complete Platform Architecture Blueprint Index.md`
- `Hybrid Janavani WebSite.md`
- `The dynamic architecture.md`
- `Multi-Service Stack Orchestration.md`
- `Step-by-Step Production Launch Runbook.md`

The current architecture is represented by the canonical documents listed in Section 1.
