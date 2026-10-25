# Telegram Post-Commit Replay Acceptance Contract

Status: required acceptance gate; not yet proven end-to-end.

## Invariant

Telegram webhook delivery is at-least-once. The current candidate processes each new parsed update in request memory, while PostgreSQL stores a content-free receipt keyed by Telegram `update_id`. The HTTP request receives a success response only after the handler and durable receipt completion succeed. Processing failures return a retryable non-2xx response.

A process may still crash after a business transaction commits but before the receipt is marked processed or the response reaches Telegram. Redelivery must not duplicate consequential business effects. Inbox receipt deduplication is necessary but insufficient; the canonical business mutation still needs durable idempotency.

## Required test scenario

Run against the same PostgreSQL-backed Case/Submission mutation path used by the Telegram application:

1. Receive a valid Telegram update and claim a PostgreSQL receipt containing the `update_id`, status and attempt/lease metadata only; assert `payload IS NULL`.
2. Dispatch the parsed update through the real Telegram handler from request memory and commit one canonical business mutation.
3. Inject a crash/failure after the business transaction commits but before `mark_processed` or the HTTP success response is confirmed.
4. Return or simulate a retryable non-2xx/lost response, allow the content-free receipt claim to become reclaimable, and redeliver/reprocess the same Telegram `update_id`.
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

- New webhook deliveries must not write full Telegram update JSON or citizen narrative to PostgreSQL. The receipt-only method accepts the update ID, not the payload.
- The background worker may claim only payload-bearing compatibility rows from the old implementation; it must not claim receipt-only rows.
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

The PostgreSQL inbox tests now cover content-free receipt storage, duplicate update-ID detection, inline receipt claim completion and stale-claim fencing; separate compatibility tests cover old payload-bearing queue rows. The existing Submission/Case transaction integration test proves atomic mutation and durable replay at the repository boundary. These tests do not, separately or together, prove the handler crash between business commit and HTTP acknowledgement. This contract must remain open until the real-handler replay test above passes in CI without being skipped.
