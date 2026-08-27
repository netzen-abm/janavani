# JANAVANI — CANONICAL REPOSITORY SERIALIZATION CONTRACT

**Date:** 27 August 2026  
**Status:** IMPLEMENTATION GUIDANCE / VERIFICATION GATE  
**Scope:** Case, Evidence, Authority, Consent, Document, Submission and delivery events

## Purpose

Define the repository boundary between the canonical Python domain objects and the durable PostgreSQL/Supabase representation.

The repository layer owns persistence mapping. Domain objects remain provider-neutral and must not contain Supabase client calls.

## Canonical mapping

| Domain object | Durable table | Identity | Important rule |
|---|---|---|---|
| `Case` | `cases` | `id` | Lists are represented by explicit relationship tables |
| `Evidence` | `evidence` | `evidence_id` | Binary content remains behind `content_ref` |
| `Authority` | `authorities` | `authority_id` | Verification requires source provenance |
| `Consent` | `consents` | `consent_id` | Purpose/scope/policy version preserved |
| `Document` | `documents` | `document_id` | Artifact/hash references preserved |
| `Submission` | `submissions` | `submission_id` + `operation_id` | Operation identity is stable across retries |
| `CaseEvent` | `case_events` | generated event id | Append-only audit observation |
| `DeliveryEvent` | `delivery_events` | generated event id | Never infer remote receipt from queue state |

## Serialization rules

1. Enum values persist using their canonical string values.
2. UTC timestamps persist as PostgreSQL `timestamptz`.
3. Domain IDs are preserved exactly; repositories must not silently generate replacement IDs on update.
4. Relationship lists are normalized through relationship tables rather than duplicated JSON arrays.
5. Structured metadata may use `jsonb` where no stable relational contract has yet been established.
6. Evidence/document payload bytes are not placed into ordinary case rows; durable records store references/hashes.
7. Consent references must remain traceable to the capability, purpose, source channel and policy version that produced them.
8. Submission `operation_id` is unique and must survive retry attempts.
9. Delivery state is derived from explicit delivery events and the current submission status; a local queue is never equivalent to `RECEIVED`.
10. Repository methods must surface provider/database failures rather than converting them to synthetic domain success.

## Transaction boundaries

A repository operation should be atomic for its own aggregate boundary.

For consequential submission creation, the application workflow should persist the submission and its case reference consistently before handing the operation to an outbound transport queue.

Transport transmission is a separate operation and must append explicit delivery events.

## Security boundary

Repositories do not grant authorization. Authorization, permission and consent checks remain application/API responsibilities.

RLS is enabled by the initial schema migration without permissive public policies. Production policies must be designed and verified before durable data is exposed through Supabase client roles.

## Verification gate

The following are required before replacing the current `NotImplementedError` repository adapters with production Supabase calls:

- canonical migration applied successfully in a controlled environment;
- round-trip tests for each domain object;
- relationship integrity tests;
- transaction/rollback tests;
- RLS tests for intended roles;
- duplicate/idempotency tests for submissions;
- delivery-state integrity tests;
- no synthetic success on provider/database errors;
- actual CI execution evidence;
- deployment configuration evidence.

Until those gates pass, the Supabase repository remains an explicit boundary rather than a claimed production implementation.
