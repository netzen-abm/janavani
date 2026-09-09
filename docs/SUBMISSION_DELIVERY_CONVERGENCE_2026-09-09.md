# Janavani — Submission/Delivery Convergence Record

**Date:** 9 September 2026
**Status:** VERIFYING

## Decision

The current repository already contains the canonical Case lifecycle states for `SUBMITTING`, `QUEUED`, `SUBMITTED`, and `ACKNOWLEDGED`. It also has a separate canonical document artifact boundary. Therefore no second document-delivery engine was introduced.

A provider- and surface-neutral `SubmissionCapability` was added at `src/capabilities/submission.py`.

## Boundary

The capability requires all of the following before external transmission:

1. authenticated identity owning the Case;
2. attached canonical document reference;
3. non-empty destination reference;
4. explicit user approval for the consequential operation;
5. capability authorization for `case:submit`;
6. valid granted consent for purpose `case_submission` and the requested scope.

The transport is an adapter implementing `SubmissionTransport`. It does not become the domain authority.

## Lifecycle semantics

```text
READY
  ↓ explicit user approval + authorization + consent
SUBMITTING
  ↓ transport accepts
SUBMITTED
  ↓ destination acknowledgement exists
ACKNOWLEDGED
```

A transport failure leaves the Case at `SUBMITTING`; Janavani does not claim delivery or acknowledgement.

A successful transport without an acknowledgement reference records `SUBMITTED`, not `ACKNOWLEDGED`.

Document generation remains independent of submission. A generated/attached document does not imply transmission.

## Verification tests added

`tests/test_submission_capability.py` covers:

- explicit user approval is mandatory;
- missing consent is fail-closed;
- transport failure cannot produce a false success state;
- acknowledgement is recorded only when returned by the transport;
- document attachment alone does not imply submission.

## Repository commits

- `a4e7ce2fbf913269743942eb140a57ab349a78c2` — initial submission capability boundary.
- `082cb5068490cff5f1a0b618d68564821a4bdc7f` — corrected submission boundary to use the public Case persistence method.
- `0c0911edcdb1b06dc52dd642d9312a0b297d0dfd` — added safe owned Case persistence after adapter-side failure.
- `cd8cc173f7d154a8eb7b0b130da4007637498ce1` — added focused submission safety tests.

## Open verification gate

GitHub reports no workflow run yet for the latest test commit `cd8cc173f7d154a8eb7b0b130da4007637498ce1`. Therefore this record does **not** claim CI-green status for the new submission capability yet.

The next verification step is to run the repository's canonical CI/test suite and fix only failures caused by this change. Existing unrelated lint debt must not be conflated with submission correctness.

## Archive/convergence rule

Historical submission/delivery implementations remain preserved. No branch or historical implementation is deleted merely because this capability now exists. Further retirement requires dependency, replacement, runtime, test, and historical-preservation evidence.
