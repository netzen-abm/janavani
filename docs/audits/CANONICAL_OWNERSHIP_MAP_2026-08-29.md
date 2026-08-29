# Canonical Ownership Map — 2026-08-29

## Purpose

Prevent repository growth through duplicate implementations. Every shared capability must have one canonical contract/owner; providers and access surfaces consume it through adapters.

## Canonical platform ownership

| Capability | Canonical owner | Provider/access implementations | Decision |
|---|---|---|---|
| Case | `src/domain/case.py` + `src/application/case_workflow.py` | memory/Supabase repositories | KEEP + CONVERGE |
| Evidence | `src/domain/evidence.py` + capability layer | storage adapters | KEEP + CONVERGE |
| Authority | `src/domain/authority.py` + `src/services/authority_service.py` | channel adapters | KEEP + CONVERGE |
| Document | canonical domain/capability layer | render/export adapters | CONVERGE |
| Submission | `src/domain/submission.py` + workflow | delivery adapters | KEEP + CONVERGE |
| Tracking | `src/core/platform_contracts.py` | memory/database/channel adapters | KEEP |
| Provenance | `src/core/platform_contracts.py` | memory/database adapters | KEEP |
| Notifications | `src/core/platform_contracts.py` | channel adapters | CONTRACT FIRST |
| Storage | repository contracts + provider adapters | memory/JSONL/Supabase/etc. | CONVERGE |
| AI | provider-neutral gateway | provider adapters | CONTRACT FIRST |
| Safety/Policy | shared policy boundary | surface-specific UX | CONTRACT FIRST |

## Access surfaces

Web, mobile, Telegram, WhatsApp, Messenger, API and decentralized clients are access surfaces/adapters. They must not become owners of Case/Evidence/Authority/Document/Submission business rules.

## Generational code policy

- Empty placeholders: delete after SHA verification.
- Real duplicate implementations: converge into the canonical owner.
- Historical but uncertain implementations: isolate/archive.
- Confirmed obsolete implementations: archive first, delete only after dependency evidence.

## Current audit observations

The repository contains multiple historical web/runtime/storage/service generations. Their presence alone is not sufficient evidence for deletion. Runtime entrypoints, imports, deployment configuration and tests must be checked before archiving.

## Completion definition

A capability is canonical only when its contract, implementation, tests, integration path and documentation agree. A directory name alone does not establish ownership.
