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


## Hard ecosystem rule — no Janavani personal-data repository

Janavani must not create or maintain a durable repository of citizen personal or sensitive information. In particular, Janavani persistence must not contain citizen names, addresses, phone numbers, email addresses, government identifiers, identity documents, biometric data, precise personal location history, private communications, evidence originals, or raw citizen narratives.

### Device-first content boundary

- WebApp drafts, raw narratives, evidence originals and generated documents remain on the citizen device where technically possible.
- A Telegram bot necessarily receives Telegram messages transiently; this is transport processing, not permission to persist the content. Telegram-originated personal/sensitive content must not be copied into durable Janavani storage, logs, analytics, telemetry or reusable profiles.
- If an operation requires information to leave the device, the transfer must be purpose-bound, minimized, explicitly authorized where required, encrypted in transit and limited to the selected destination/processor.
- Durable Janavani Case state should contain only opaque identifiers and minimum non-sensitive lifecycle metadata. Raw citizen content belongs outside the durable Case repository.
- Scraping or enrichment must never be used to silently discover, infer or accumulate personal/sensitive citizen data. External public information may be collected only for the selected capability and must remain distinguishable from citizen-provided information.

### Architectural consequence

The Case aggregate is a civic workflow/control record, not a personal-data vault. Any future capability that requires raw citizen content must define a separate transient/device-local content boundary and must prove that the content is not persisted by Janavani before integration.


## Persistence-boundary enforcement

The privacy rule is enforced at the provider boundary, not only by callers. Case persistence adapters must redact citizen subject/narrative content before durable storage. A caller passing raw content to a repository must therefore not be able to turn the Case repository into a citizen-content store.

The same principle applies to document/evidence artifacts: references and hashes may be retained when required for a selected lifecycle capability, but citizen document/evidence payloads must remain device-local or transiently destination-bound unless a separate, explicit retention contract is approved.

### Identity minimization

A surface identifier such as a Telegram user ID is not a general-purpose citizen identity record. Cross-surface continuity should prefer citizen-held opaque capability proofs/tokens over a durable channel-to-citizen profile. Any persistent identity link requires a separate privacy/security contract and explicit necessity.
