# Capability Activation Policy

## Status
Implemented as a platform composition gate on the dedicated feature branch.
Submission remains disabled on ordinary citizen-facing surfaces. No production
approval or external delivery authorization is granted by this implementation.

## Principle
A capability's existence in source code, or injection of a transport/dependency,
does not grant permission to activate it. Platform activation is separate from and
supplemental to domain authorization, consent, explicit approval, idempotency,
execution-context validation, and audit requirements.

## Policy dimensions
The immutable policy snapshots the supplied activation mapping at construction and
records runtime environment and surface, plus per-capability:
- stable capability identifier;
- maturity: designed, implemented, composed, integration_verified,
  production_approved, suspended, or retired;
- enabled/disabled state;
- permitted surfaces and environments;
- dependency verification;
- accountable owner;
- explicit approval reference.

The policy denies activation when any required condition is missing or mismatched.
Production requires production_approved maturity. Non-production activation requires
at least integration_verified maturity.

## Current submission posture
- Capability: `case:submit`
- Default activation: absent/disabled
- Ordinary Web and Telegram compositions: no submission capability is injected
- External delivery: not authorized
- Production approval: not granted

The citizen-facing document workflow remains Prepare -> Review -> Approve -> Download.
The citizen independently sends the document. Download, reminder, or document
approval is not evidence of external submission.

## Consent boundary
`case_submission` remains reserved for explicit external delivery consent.
The canonical consent capability now records `document_preparation` separately for
preparing a document that the citizen downloads and sends independently. Preparation
consent does not authorize external delivery, advance the Case lifecycle, or imply
that a document was submitted. External delivery requires its own purpose- and
scope-bound consent plus the separate activation and execution gates.

Historical consent records are not reinterpreted or migrated by this change. Existing
`case_submission` records retain their original meaning; no record is silently
converted into preparation consent.

## Verification
Automated tests cover missing/disabled policy, maturity, surface/environment scope,
dependency verification, accountability, retirement, immutable mapping snapshots,
and transport-injection bypass.

## Non-goals
This change does not create a delivery adapter, change database schemas, migrate
historical consent records, enable a worker, or authorize production deployment.
