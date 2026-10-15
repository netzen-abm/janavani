# Telegram Post-Commit Replay Acceptance Contract

Status: required acceptance gate; not yet proven end-to-end.

## Invariant

Telegram inbox delivery is at-least-once. A worker may crash after a business transaction commits and before the inbox row is marked processed. Redelivery must not duplicate consequential business effects.

Inbox deduplication by Telegram `update_id` is necessary but insufficient: it prevents duplicate acceptance, not replay of an already-claimed update.

## Required test scenario

Run against the same PostgreSQL-backed Case/Submission mutation path used by the Telegram application:

1. Accept a Telegram update durably and claim it.
2. Dispatch it through the real Telegram handler and commit one canonical business mutation.
3. Inject a crash/failure after the database commit but before `mark_processed`.
4. Allow the inbox claim to become reclaimable, then redeliver/reprocess the same accepted update.
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

The existing inbox tests prove durable acceptance, duplicate update-ID rejection, claim completion, and stale-worker fencing. The existing submission/Case transaction integration test proves atomic mutation and durable replay at the repository boundary. Those tests do not, separately or together, prove the injected worker crash between business commit and inbox completion. This contract must remain open until the end-to-end test above passes in CI.
