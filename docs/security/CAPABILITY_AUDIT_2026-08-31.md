# Janavani Capability Authorization Audit

**Date:** 31 August 2026  
**Branch:** `security/auth-boundary-hardening`

## Executive result

The audit found that the existing Telegram command layer contains both read-only and state-changing operations, but those commands currently call legacy services directly rather than passing through the shared authorization boundary.

The security branch therefore establishes a canonical capability registry and documents the required migration rather than pretending every legacy path is already protected.

## Capability classification

| Existing operation | Classification | Target capability | Anonymous? | Current enforcement |
|---|---|---|---|---|
| `/start` | informational | `public.start` | Yes | command-level only |
| `/search` | public directory lookup | `public.search_office` | Yes | **migration required** |
| `/check` | complaint status lookup | `public.complaint_status` | Yes, if only non-sensitive status is exposed | **migration required** |
| `/complaint` | workflow initialization | `citizen.complaint.start` | Yes | **migration required** |
| `/rate` | persistent civic feedback write | `citizen.rating.submit` | Yes, subject to anti-abuse policy | **migration required** |
| document generation | consequential artifact creation | `citizen.document.generate` | No by default | shared service protected |
| external document transmission | consequential external effect | `citizen.document.transmit` | No | shared authorization + consent gate |

## Important privacy/security finding

The legacy Telegram command layer uses the Telegram platform user ID as its conversation-state key. This is operational channel state and must not be promoted into the canonical `Principal` as a citizen identity. The shared identity model requires an opaque principal identifier.

## Required migration rule

Legacy commands must become thin adapters:

```text
Telegram Update
      ↓
Telegram Adapter
      ↓
IdentityContext
      ↓
Shared AuthorizationPolicy
      ↓
Capability Service
      ↓
Result
```

They must not implement independent authorization logic.

## Read operations

Public directory search can remain anonymous if the returned dataset is intentionally public. Complaint-status lookup can remain anonymous only when the complaint identifier itself is the intended access secret and the returned fields are non-sensitive; otherwise an additional possession/identity control is required.

## Write operations

Rating submission may remain anonymous because the product can accept civic feedback without a citizen account, but it needs abuse controls (rate limiting, validation and input constraints). A successful write must not be represented as government submission.

## Consequential operations

Document generation and especially external transmission remain protected capabilities. Transmission additionally requires explicit consent and destination authorization.

## Bypass risks to close

1. Direct calls from commands to legacy services.
2. Direct calls from scripts/tests to write services without capability context.
3. Duplicate document-generation paths.
4. Any endpoint that treats a channel credential as citizen identity.
5. Any status endpoint that reveals more information than the complaint identifier is intended to disclose.

## Decision

Do not add mandatory authentication to the entire Telegram bot. Protect capabilities according to their actual risk and data requirements. This preserves Janavani's anonymous/local-first design while preventing privileged operations from bypassing the shared trust boundary.
