# JANAVANI — AUTHENTICATION & CREDENTIAL MODEL

**Status:** DOCUMENTED — CURRENT REPOSITORY STATE
**Date:** 31 August 2026

## Current state

The current repository does not yet contain a complete conventional end-user authentication system such as a finished JWT/OAuth login, password-reset, session-revocation, or centralized citizen account service.

The repository does contain service/integration credentials and a strong privacy architecture that defines identity as capability-specific and user-controlled.

## Credential classes

| Credential | Current purpose | Citizen login credential? |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot integration | No |
| `SUPABASE_URL` | Supabase integration configuration | No |
| `SUPABASE_ANON_KEY` | Supabase client/integration access | No |
| `OPENROUTER_API_KEY` | OpenRouter provider access | No |
| `HF_TOKEN` | Hugging Face inference/provider access | No |
| `NOSTR_PRIVATE_KEY_HEX` | Nostr cryptographic identity | Capability-specific |
| `CHAIN_PRIVATE_KEY` | Blockchain signing authority | Capability-specific |

## Secret handling

Secrets are represented by environment-variable names in `.env.example`. The populated `.env` must remain outside the repository. Secrets must not be embedded in client source, logs, URLs, telemetry, crash reports, or public bundles.

## Current request model

```text
Citizen / External Actor
        ↓
Independent Interface / Integration
        ↓
Shared Janavani Platform Contracts
        ↓
Domain + Workflow + Capability
        ↓
Optional service credential / cryptographic key
        ↓
External provider or destination
```

This is capability authentication, not a completed universal citizen-login flow.

## Intended identity model

Janavani defines three practical identity modes:

1. **Anonymous** — no persistent Janavani identity where the capability does not require one.
2. **Local identity** — identity information stays on the citizen device unless explicitly transmitted for a selected capability.
3. **Authenticated identity** — used only where persistent continuity, recovery, synchronization, delegation, or another justified security property requires it.

Cryptographic identities such as Nostr keys or blockchain keys are separate capability credentials and must not automatically become a universal Janavani account identity.

## Authentication versus authorization

The future shared Identity, Access & Trust contract separates:

```text
Identity
   ↓
Authentication
   ↓
Authorization
   ↓
Capability permission
   ↓
Consent / approval
   ↓
Destination authorization
   ↓
Execution
   ↓
Outcome / provenance
```

Authentication alone must never grant access to unrelated capabilities or imply consent to transmit personal data.

## Future protected-request flow

```text
Interface / Adapter
        ↓
Identity context
        ↓
Authentication, if required
        ↓
Capability + action
        ↓
Authorization policy
        ↓
Consent / approval, if required
        ↓
Data minimization + provenance
        ↓
Capability execution
        ↓
Selected external destination
        ↓
Outcome / audit
```

## Security requirements for future sessions/tokens

Where authenticated sessions are implemented, Janavani should use short-lived access credentials, protected and revocable refresh credentials where applicable, explicit expiry, audience/issuer validation, least-privilege scopes, session/device revocation, and secure browser storage. Browser sessions should prefer secure HttpOnly SameSite cookies where the architecture permits.

Tokens must not be accepted merely because they are syntactically valid. Signature, issuer, audience, expiry, scope and applicable revocation state must be checked.

## Privacy boundary

Authentication must not undermine the privacy architecture. Janavani must not require a central personal-data repository merely to provide capabilities that can safely operate anonymously or locally.

Personal information should remain on the citizen device whenever practical and should leave the device only for an explicitly selected capability using an encrypted transport and a minimized payload.

## Implementation status

- Identity & Access & Trust contract: **DESIGNED**
- Conventional citizen login: **NOT YET IMPLEMENTED / NOT VERIFIED**
- Shared authorization middleware: **NOT YET VERIFIED**
- Token/session lifecycle: **NOT YET VERIFIED**
- Service credential environment model: **PRESENT**
- Privacy identity model: **DOCUMENTED**
- Production security verification: **NOT YET COMPLETE**

## Related canonical documents

- `docs/SOURCE_OF_TRUTH.md`
- `planning/IDENTITY_ACCESS_TRUST_CONTRACT.md`
- `planning/PRIVACY_ARCHITECTURE.md`
- `SECURITY.md`

## Rule

**Do not describe Janavani as having complete user authentication until implementation, tests, deployment verification, security verification, and documentation reconciliation have all been completed.**
