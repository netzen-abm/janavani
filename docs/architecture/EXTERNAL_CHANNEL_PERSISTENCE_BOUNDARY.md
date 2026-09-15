# External Channel Persistence Boundary

## Decision

The external-channel registry is canonical metadata used by the civic-action submission boundary. It therefore belongs to the shared provider-composition plan as the `external_channel` persisted domain.

The current implementation intentionally supports only the `memory` provider. This is appropriate for the present development/runtime stage because the repository does not yet contain a verified durable source, registration lifecycle, schema/migration contract, or authoritative channel-maintenance workflow.

## What is canonical

`ExternalChannel` records:

- canonical channel identifier;
- authority ownership;
- channel type;
- destination reference;
- jurisdiction;
- source provenance;
- verification timestamp and status;
- optional notes.

The core contract is provider-neutral and read-only. It does not perform routing, authorization, delivery, submission, or external side effects.

## Why we do not add PostgreSQL yet

A durable adapter would create more than persistence. It would require an evidence-backed source of truth and a lifecycle for creating, verifying, revoking, and updating channels. The current repository does not establish those requirements.

Adding PostgreSQL merely for provider symmetry would be architectural overreach. The shared provider plan can already name `external_channel`; the bounded adapter is deferred until product requirements justify it.

## Fail-closed behavior

If a non-implemented durable provider such as `postgres` is selected explicitly for `external_channel`, composition raises a configuration error rather than silently falling back to memory. This prevents an apparently durable deployment from using process-local channel metadata.

## Required evidence before a durable adapter

Before adding a durable adapter, establish:

1. authoritative channel source and provenance requirements;
2. registration/update/revocation lifecycle;
3. schema and migration contract;
4. verification/audit semantics;
5. transaction requirements with submission, if any;
6. provider-specific adapter and conformance tests.

Until then, `memory` remains the explicit development provider and no channel data is deleted or transformed.
