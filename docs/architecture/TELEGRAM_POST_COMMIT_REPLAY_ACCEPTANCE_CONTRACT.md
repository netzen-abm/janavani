# Telegram Post-Commit Replay Acceptance Contract

Status: required acceptance gate; not yet proven end-to-end.

## Invariant

Telegram webhook delivery is at-least-once, but provider retry windows are not a durable application queue. The webhook now encrypts each parsed update using the configured Fernet key ring before inserting it into PostgreSQL, then returns HTTP 202 only after the encrypted payload is durably accepted. A separate worker decrypts the payload in memory, dispatches it through the real handler, and clears ciphertext on success or terminal dead-letter. Transient processing failures retain ciphertext for bounded worker retries, subject to the 24-hour processing deadline.

A process may still crash after a business transaction commits but before the inbox row is marked processed. The worker can reclaim the encrypted payload after the lease expires; redelivery must not duplicate consequential business effects. Queue encryption protects payload confidentiality at rest, but inbox deduplication is not business-effect idempotency.

**Conversation-state limitation:** `src/conversation/session.py` and `src/conversation/state.py` currently keep workflow metadata and the 15-minute issue buffer only in process memory. The encrypted queue can recover an update body after a worker restart, but does not by itself restore the conversation step or `case_id`. Therefore a retry must not be described as a resumed citizen journey. The real-handler acceptance must simulate a restart with empty local state and prove either that an approved minimal, non-narrative session can be restored or that the handler fails closed with clear restart/recovery guidance without duplicating/orphaning a Case or claiming success.

## Required test scenario

Run against the same PostgreSQL-backed Case/Submission mutation path used by the Telegram application:

1. Accept a valid Telegram update and assert PostgreSQL stores `payload IS NULL`, a non-NULL Fernet ciphertext, and an expiry no more than 24 hours after acceptance; assert the plaintext marker is absent from the stored bytes.
2. Claim/decrypt the update through the existing inbox worker and dispatch it through the real Telegram handler and canonical capability, committing one business mutation.
3. Inject a crash/failure after the business transaction commits but before `mark_processed`.
4. Allow the claim lease to expire, reclaim and decrypt the same update from PostgreSQL, then assert exactly one durable Case/Submission mutation and one lifecycle event.
5. Assert the canonical Case projection and version, Submission projection and version, and lifecycle-event count are unchanged by the replay.
6. Assert external or other consequential effects are deduplicated by a durable idempotency boundary or are safely repeatable. Do not treat a mocked counter alone as proof of production behavior.
7. Assert the inbox eventually reaches `processed`, and a conflicting reuse of the business idempotency key is rejected.
8. Repeat the verification using a fresh worker/repository instance to rule out process-local memory as the deduplication mechanism.

## Required evidence

- PostgreSQL-backed integration test using the real handler/capability and durable repository path.
- CI result for that exact commit with the new test executed (not skipped).
- Assertions against durable rows after replay, including exactly one lifecycle event for the operation.
- No production deployment or merge based only on an in-memory shared-capability test.

## Design constraints

- New webhook deliveries must never write plaintext Telegram JSON to PostgreSQL. `accept_encrypted()` persists a Fernet ciphertext and an expiry; the key ring lives in a separately configured secret, never in the database or source.
- The existing worker claims both newly encrypted rows and legacy plaintext rows. Startup encrypts legacy payloads before registering the webhook; expired rows are terminalized and cleared.
- Ciphertext is cleared after success or terminal failure. If the worker is offline at expiry, cleanup occurs when it resumes; the deadline prevents processing after expiry but is not a hard external storage TTL while every worker is offline.
- Rotate keys by adding the new key first in `JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS` and retaining previous keys until their payloads and backups no longer require them.
- Reuse the canonical Case/Submission transaction and idempotency contracts where they already enforce the invariant.
- Do not add a second generic idempotency framework or process-local deduplication as the correctness mechanism.
- Keep Telegram transport, webhook acceptance, inbox worker, and business mutation responsibilities separate only at their existing trust/runtime boundaries.
- Preserve at-least-once delivery semantics; do not claim exactly-once delivery. The target is effectively-once business effects through durable idempotency.

## Adjacent end-to-end acceptance

In the same test environment, prove:
- Web creates a durable Case.
- A paired, authenticated Telegram identity retrieves that same Case.
- A different identity cannot retrieve it.
- Case/document/evidence references and consent/submission-preparation state remain truthful after process restart.
- Worker/API restart does not lose accepted updates or committed Case state.

## Current limitation

The PostgreSQL inbox tests now cover ciphertext-at-rest, plaintext absence, duplicate update-ID detection, encrypted worker claim/decryption, bounded expiry, retry ciphertext retention, terminal payload clearing, legacy-payload migration and stale-claim fencing. These tests do not, separately or together, prove the real-handler crash between business commit and `mark_processed`. This contract must remain open until the handler-level PostgreSQL replay test above passes in CI without being skipped.
