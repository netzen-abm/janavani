# Rust Domain Parity Hardening

## Purpose

This document records the verified hardening boundary for the canonical Rust `CivicCase` aggregate after the lifecycle and aggregate model were established.

The objective is to make Rust the reference domain implementation without silently changing existing Python semantics.

## Verified defects to correct before treating the aggregate as hardened

### 1. Event notes must be persisted on the stored event

`CivicCase::acknowledge()` currently calls `status_event()` and then adds `notes` to the returned event. The event already stored in `self.events` therefore retains `notes = None`.

Required invariant:

- the returned event and the event appended to `self.events` represent the same event data;
- acknowledgement notes belong in `CaseEvent.notes`;
- `source_ref` remains reserved for an external source/reference identifier.

### 2. Notes and source references must remain semantically distinct

The current `status_event()` signature accepts `source_ref`, while several domain operations pass their `notes` argument into that position (`follow_up`, `respond`, `resolve`, `escalate`, and `correct`).

Required invariant:

- `source_channel` identifies the originating channel;
- `source_ref` identifies an external/source-system reference;
- `notes` carries human-readable event context;
- domain operations must never overload one field as another.

### 3. Aggregate mutation must be atomic with event recording

Several operations change `self.status` or reference collections before `record()` can reject the event (for example, a duplicate event ID).

Required invariant:

> A rejected domain operation must leave the aggregate unchanged.

The first implementation should use a validate/build/commit sequence: validate all preconditions, construct the event, validate event uniqueness, then mutate the aggregate and append the event as one logical operation.

## Deliberate non-goals

This hardening step does **not**:

- add persistence;
- add HTTP, Telegram, Web, AI, or UI dependencies;
- invent `IN_PROGRESS` or `ARCHIVED` mutations;
- change the canonical lifecycle graph;
- redesign evidence storage;
- introduce server-side binary evidence storage;
- change the provider-neutral application boundary.

## Acceptance criteria

1. Every event field has one semantic meaning.
2. Stored and returned events are identical for a successful mutation.
3. Failed mutations do not partially mutate the aggregate.
4. Existing Python/Rust contract-equivalence tests remain green.
5. The lifecycle semantic boundaries documented in `CASE_LIFECYCLE_SEMANTICS.md` remain unchanged.

Only after these criteria are met should the next domain capability—Evidence—be promoted into the canonical Rust kernel.
