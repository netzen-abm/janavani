# Canonical Provider Composition

## Purpose

Janavani has multiple access surfaces and multiple persistence boundaries. Provider selection must therefore be a shared infrastructure concern, not a decision made independently by Telegram, web, mobile, agents, or other surfaces.

The canonical boundary is `src/storage/provider_composition.py`.

## Contract

`ProviderComposition` is an immutable provider plan for persisted domain boundaries. It:

- defines the persisted domains recognized by the platform;
- defaults safely to `memory` for development;
- resolves environment configuration without importing provider adapters;
- exposes `provider_for(domain)` as the shared provider decision;
- supports immutable single-domain overrides through `with_provider()`;
- rejects unknown domains and empty provider names;
- does not create database clients;
- does not perform migrations;
- does not make decision-only capabilities persistent merely for symmetry.

`src/platform/composition.py` now creates this plan and routes Civic Case repository creation through it. The existing direct Civic Case provider API remains available for compatibility and tests.

## Current persisted domains

- `civic_case`
- `consent`
- `evidence`
- `document_artifact`
- `document_review`
- `authority`
- `policy`
- `submission`
- `accountability_feedback`
- `external_channel`

Listing a domain here does **not** claim that every domain already has a PostgreSQL adapter. The composition boundary describes the platform's persistence surface; adapter availability remains domain-specific and must be verified before a durable provider is selected.

## Provider policy

For the current free/development phase:

1. keep the default composition memory-first;
2. do not require PostgreSQL configuration merely to run the product;
3. do not introduce another generic storage adapter;
4. add a bounded adapter only when a domain actually needs durable persistence;
5. use shared Unit-of-Work semantics where multiple canonical records must commit atomically;
6. keep external delivery outside database transactions;
7. retain legacy JSONL/CSV sources until migration evidence supports retirement.

## Next convergence step

The next provider work should extend this boundary to the remaining persisted capabilities only when their repository contracts are mature enough to justify durable implementations. The first candidates are Accountability Feedback and External Channel, because they are canonical persisted boundaries but currently lack PostgreSQL repository/provider equivalents.

This document does not authorize production migration. Production migration remains gated by verified target schema, migration history, RLS/authorization policy, identity mapping, backup/recovery, and controlled cutover evidence.
