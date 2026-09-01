# Canonical Case Storage & Privacy Contract

## Status
Proposed integration contract for the canonical platform foundation.

## Purpose
Define the storage boundary for CivicCase before connecting durable persistence.

## Principles
- The CivicCase domain remains storage-agnostic.
- Personal and sensitive citizen content remains on the user device by default.
- A persistence adapter must receive only the minimum data required for the selected capability.
- Encryption does not itself authorize transmission.
- Server-side storage is never a prerequisite for drafting, review, correction, printing, or downloading a civic document.
- A storage adapter must not silently create a citizen-wide identity graph.
- Channel adapters must not persist their own parallel case representations.

## Field classification
| Field | Default class | Server persistence by default |
|---|---|---|
| `case_id` | capability identifier | No; only if required by selected remote workflow |
| `case_type` | non-sensitive workflow metadata | Minimum necessary only |
| `subject` | citizen content; may be sensitive | No |
| `narrative` | citizen content; may be sensitive | No |
| `created_by` | identity-linked metadata | No |
| `related_office_id` | non-personal operational metadata | Minimum necessary only |
| `evidence_refs` | relationship metadata | No unless explicitly required |
| `document_refs` | relationship metadata | No unless explicitly required |
| `consent_refs` | policy/security metadata | Minimum necessary only |
| `status` | workflow metadata | Minimum necessary only |
| `events` | audit/provenance metadata; may contain sensitive notes | No by default |

## Adapter contract
A storage adapter must support explicit capability-scoped reads/writes. It must not infer permission from mere possession of a case object.

## Compatibility
JSONL, Supabase/PostgreSQL, encrypted remote storage, decentralized storage, and future adapters are implementation choices behind the same contract. No adapter is canonical merely because it is available.

## Verification gates
Before durable persistence is enabled for citizen data, verify:
1. field-level minimization;
2. encryption at rest and in transit where applicable;
3. authorization and consent boundaries;
4. logging/telemetry redaction;
5. retention/deletion behavior;
6. recovery behavior;
7. absence of unintended cross-capability replication;
8. end-to-end evidence for the selected adapter.
