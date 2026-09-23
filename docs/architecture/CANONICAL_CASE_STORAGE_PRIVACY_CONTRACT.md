# Canonical Case Storage & Privacy Contract

## Status

Canonical ecosystem storage/privacy contract.

## Principles

- CivicCase remains storage-agnostic.
- Personal and sensitive citizen content remains local by default.
- Persistence adapters receive only the minimum data required by the selected capability.
- Encryption does not itself authorize transmission.
- Server-side storage is not a prerequisite for drafting, review, correction, printing, or downloading.
- Storage adapters must not silently create a citizen-wide identity graph.
- Web, Telegram and other channel adapters must not persist parallel case representations.

## Field classification

| Field | Default class | Server persistence by default |
|---|---|---|
| `case_id` | capability identifier | No; only when required by selected remote workflow |
| `case_type` | non-sensitive workflow metadata | Minimum necessary only |
| `subject` | citizen content; may be sensitive | No |
| `narrative` | citizen content; may be sensitive | No |
| `created_by` | identity-linked metadata | No |
| `related_office_id` | operational metadata | Minimum necessary only |
| `evidence_refs` | relationship metadata | No unless explicitly required |
| `document_refs` | relationship metadata | No unless explicitly required |
| `consent_refs` | policy/security metadata | Minimum necessary only |
| `status` | workflow metadata | Minimum necessary only |
| `events` | audit/provenance metadata; may contain sensitive notes | No by default |

## Adapter contract

A storage adapter must support explicit capability-scoped reads/writes. Possession of a case object must never itself imply permission to read or mutate it.

## Verification gates

Before durable citizen-data persistence is enabled:

1. field-level minimisation;
2. encryption at rest and in transit where applicable;
3. authorization and consent boundaries;
4. telemetry redaction;
5. retention/deletion behaviour;
6. recovery behaviour;
7. absence of unintended cross-capability replication;
8. end-to-end evidence for the selected adapter.
