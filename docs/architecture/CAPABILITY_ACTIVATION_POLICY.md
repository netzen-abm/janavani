# Capability Activation Policy

## Status
Implemented as a deny-by-default platform composition and submission-boundary
gate on the dedicated feature branch. Submission remains disabled on ordinary
citizen-facing surfaces. No production approval or external delivery authorization
is granted by this implementation.

## Principle
A capability's existence in source code, or injection of a transport/dependency,
does not grant permission to activate it. Platform activation is separate from and
supplemental to domain authorization, consent, explicit approval, idempotency,
execution-context validation, and audit requirements.

## Policy dimensions and runtime binding
The immutable policy snapshots the supplied activation mapping and records the
process runtime environment and surface, plus per-capability:
- stable capability identifier;
- maturity: designed, implemented, composed, integration_verified,
  production_approved, suspended, or retired;
- enabled/disabled state;
- permitted surfaces and environments;
- dependency verification;
- accountable owner;
- explicit approval reference.

The process environment is read from `JANAVANI_RUNTIME_MODE` through
`src/config/runtime.py`. Only `development`, `test`, and `production` are
supported. The policy constructor rejects an environment that differs from the
actual process mode; `permits()` checks the current process mode again at the
decision point and denies if it has changed or is invalid. Unknown values and
aliases such as `prod` and `staging` fail closed. Production requires
`production_approved` maturity; development and test require at least
`integration_verified`.

## Submission enforcement
An injected `SubmissionCapability` requires a valid activation policy when the
`CivicActionVerticalSliceDependencies` object is constructed, including when
callers instantiate `CivicActionVerticalSlice` directly instead of using the
platform factory. The public `submit()` method rechecks activation immediately
before invoking the submission capability. The platform factory also rejects
transport/capability injection without an active policy. This platform gate
supplements (and does not replace) submission authorization, purpose- and
scope-bound consent, citizen approval, verified destination checks,
execution-context validation, and idempotency.

## Current submission posture
- Capability: `case:submit`
- Default activation: absent/disabled
- Ordinary Web and Telegram compositions: no submission capability is injected
- External delivery: not authorized
- Production approval: not granted

The citizen-facing document workflow remains Prepare -> Review -> Approve -> Download.
The citizen independently sends the document. Download, reminder, or document
approval is not evidence of external submission.

## Consent boundary and audit
`case_submission` remains reserved for explicit external delivery consent.
The canonical consent capability records `document_preparation` separately for
preparing a document that the citizen downloads and sends independently.
Preparation consent does not authorize external delivery, advance the Case
lifecycle, or imply that a document was submitted.

Both persistence paths record a deterministic `CONSENT_RECORDED` Case event
with consent purpose, actor, proof reference and timestamp:
- atomic consent-plus-Case repository transaction; and
- standard Case repository path used when no atomic repository is configured.

The standard path makes consent-reference/event persistence one Case repository
save. Consent storage remains a separate repository operation when no atomic
provider boundary is injected; provider-specific atomicity is not claimed by this
fallback. PostgreSQL atomic composition must use the atomic consent repository.

Historical consent records are not reinterpreted or migrated. Existing
`case_submission` records retain their original meaning; no record is silently
converted into preparation consent.

The legacy `POST /civic/cases/{case_id}/consent` attachment route no
longer accepts an arbitrary identifier. It delegates to the Consent capability,
which requires both `case:consent` and `case:write` authorization, then verifies
that the grant is persisted, owned by the authenticated principal, active,
explicit, and bound to the requested Case by its deterministic consent ID before
attaching a reference or writing an audit event. The same two authorization
requirements apply to atomic and standard repository paths. Unpersisted
identifiers, another citizen's grants, expired/revoked grants, and grants from
another Case are rejected. New grants continue to be created through the
explicit-consent workflow.

## Verification
Automated tests cover process/runtime mismatch rejection, runtime recheck at
decision time, invalid process modes, missing/disabled activation, maturity,
surface/environment scope, dependency verification, accountability, retirement,
immutable mapping snapshots, direct-slice construction bypass, submit-time policy
recheck, persisted-grant ownership and Case binding, both consent authorization
capabilities, and audit event idempotency on standard and atomic consent paths.

## Non-goals
This change does not create a delivery adapter, change database schemas, migrate
historical consent records, enable a worker, or authorize production deployment.
