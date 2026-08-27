# Canonical DB Implementation Plan — 2026-08-27

## Objective

Move the canonical Case workflow from in-memory repositories to durable Supabase/PostgreSQL storage without changing application/domain contracts.

## Current contract

- `CaseRepository`: `get`, `save`
- `EvidenceRepository`: `save`
- `AuthorityRepository`: `get`
- `SubmissionRepository`: `get`, `save`
- pure row serialization lives in `src/storage/serialization.py`
- canonical SQL schema lives in `supabase/migrations/20260827_0001_canonical_case_workflow.sql`

## Required implementation order

1. Add row-to-domain hydration helpers alongside existing row serializers.
2. Implement parameterized Supabase repository operations using the existing client abstraction.
3. Persist relationship references and append-only events in the same application operation where required.
4. Add repository contract tests using a fake Supabase client.
5. Add a live integration test that runs only when explicitly configured with a test Supabase project.
6. Design and test RLS policies before exposing durable records through production API credentials.
7. Add migration/rollback and backup/restore verification.
8. Switch the canonical FastAPI dependency from memory repositories only after all gates pass.

## Non-goals

- Do not move business state transitions into SQL triggers.
- Do not expose service-role credentials to clients.
- Do not treat a successful local database write as external submission delivery.
- Do not migrate or delete legacy CSV/JSONL data in this migration.

## Gate

Production durable storage is **not complete** until schema, repository implementation, RLS, integration tests, operational recovery, and CI evidence are all present.
