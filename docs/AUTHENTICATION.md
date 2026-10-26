# JANAVANI — AUTHENTICATION, ACCOUNT OPTIONS & CREDENTIAL MODEL

**Status:** IMPLEMENTATION IN PROGRESS — PROVIDER SETUP AND PRODUCTION VERIFICATION REQUIRED
**Reviewed:** 26 October 2026

## Product rule

Janavani must be useful before a citizen creates an account. A person may describe an incident and prepare a complaint, an RTI application, or both without logging in. Persistent accounts are optional and exist for justified features such as Case tracking, cross-device continuity, recovery, and explicit identity linking.

Authentication identifies a caller. It does not, by itself, grant access to Cases, authorize a submission, or imply consent to send personal data to a public authority.

## Citizen-facing journey

1. **Start anonymously.** Narrate the incident, review the suggested document type, edit the draft, and download it. The anonymous drafting route must not create a persisted Case or claim that a complaint or RTI has been filed.
2. **Choose whether to keep a tracked Case.** Account creation and identity linking must be explicit and optional. A citizen may continue using anonymous drafts after choosing not to sign in.
3. **Choose a supported sign-in method.** Only methods that are configured, verified, tested, and deployed may be presented as available. An unconfigured provider must fail closed without disabling anonymous drafting.
4. **Link additional identities only by explicit confirmation.** Linking a Telegram identity to an existing Web account must prove control of both sides, expire challenges, prevent reuse, and record the link against the same opaque Janavani principal.
5. **Authorize each protected action separately.** Ownership checks and capability policy remain mandatory after authentication. Authentication alone never grants administrative or unrelated capabilities.

## Current implementation status

| Method or capability | Repository status | Availability rule |
|---|---|---|
| Anonymous incident-to-complaint/RTI drafts | Implemented on the feature branch with tests | Not a persisted Case; deployment is not yet verified |
| Web sign-in through configurable OIDC | OIDC code and session tests exist | Requires the provider and all server-side configuration; provider must support the selected login method |
| Telegram-native account sign-up via `/account` | Implemented on the feature branch with tests | Private chat only; requires the canonical composition and shared PostgreSQL external-identity store |
| Web-to-Telegram account pairing | API, Web flow, and Telegram `/pair` claim path exist | Requires authenticated Web session and shared PostgreSQL identity/pairing persistence; explicit Web confirmation is required |
| Telegram Login for Web | Provider-specific deployment/configuration not verified | Configure Telegram's supported OIDC login with the bot's allowed origins and redirect URI, or use a validated Telegram Mini App flow |
| Email one-time-code sign-in | Not implemented as a complete end-user flow | Do not advertise until delivery provider, rate limiting, verification, recovery, and tests exist |
| Mobile number / SMS one-time-code sign-in | Not implemented as a complete end-user flow | Do not advertise until phone ownership verification, abuse controls, cost limits, recovery, and tests exist |
| Generated public/private-key sign-in | Not implemented as a complete end-user flow | Do not advertise until key creation, proof-of-possession, backup/recovery, revocation, and browser/device tests exist |
| Production account lifecycle and recovery | Not fully verified | Requires live configuration, session/device revocation, recovery processes, deployment verification, and security review |

This table reflects repository inspection on 26 October 2026. It is not a claim that the feature branch is deployed. Railway's existing Python bot is currently crashing at startup, the secure webhook's required database/encryption configuration has not been verified, and a new Vercel deployment was blocked by the project's free-tier deployment quota.

## Recommended sign-in choices

### Telegram

Telegram is a good low-friction choice when a citizen already uses the bot. The bot may authenticate the Telegram platform user received through a verified Telegram update; a raw Telegram ID typed into a form is not proof of ownership. For Web login, use Telegram's supported OIDC flow configured in BotFather, or a Telegram Mini App that validates signed `initData` server-side. Never trust `initDataUnsafe` alone.

A Telegram sign-in on the Web and a Telegram bot account are not automatically the same Janavani account. To attach the bot identity to a Web account, use the existing short-lived pairing challenge and explicit confirmation flow with shared persistence. Never infer a link merely because an email, display name, or Telegram handle matches.

### Email and mobile

Use verified one-time codes or a trusted OIDC identity provider, not a bare email or phone field as proof of identity. Keep delivery-provider credentials on the server. Apply request throttles, per-destination limits, expiry, replay protection, generic error messages, recovery controls, and abuse monitoring. Keep email and phone as verified contact methods separate from the opaque principal ID.

### Public/private-key identity

A key-based identity must prove possession through a signed challenge. A public key can identify a credential, but a private key must never be uploaded as the means of authentication or stored in server logs or a normal account table. Prefer browser/device-bound passkeys or a reviewed WebCrypto/WebAuthn design with clear backup, lost-device recovery, revocation, and multi-device linking rules. If Janavani generates an exportable key pair, generate it locally, show the citizen how to protect the private key, and explain that losing it may mean loss of access unless a recovery method was configured. Do not equate possession of a blockchain/Nostr key with blanket permission to access all Janavani capabilities.

## Canonical identity and persistence boundary

- Use one opaque Janavani principal per citizen account, independent of email, phone number, Telegram subject, or public key.
- Store provider identities as unique `(provider, subject)` links to that principal. Prevent one provider identity from attaching to multiple principals.
- Verify control before linking; require an authenticated session on the account being linked and explicit user confirmation.
- Use shared PostgreSQL for identity links and cross-surface pairing. In-memory repositories are test/local-only and cannot provide durable account continuity across independently deployed Web and Telegram processes.
- Keep identity provider tokens, one-time codes, pairing codes, session cookies, private keys, and citizen narratives out of application logs and public bundles.
- Use HTTPS, HttpOnly/Secure/SameSite session cookies, a short-lived audience-bound API assertion, and least-privilege capability grants. Keep authentication, authorization, consent, destination selection, submission, and outcome recording as separate decisions.
- Anonymous drafting is transient and must not require creation of a central citizen record. Tracked Cases are created only after an explicit user decision and the canonical Case lifecycle's required checks.

## Provider configuration and release gates

The WebApp's generic OIDC flow requires all of these server-side variables:

- `JANAVANI_OIDC_ISSUER_URL`
- `JANAVANI_OIDC_CLIENT_ID`
- `JANAVANI_OIDC_CLIENT_SECRET`
- `JANAVANI_OIDC_REDIRECT_URI`
- `JANAVANI_WEB_SESSION_SECRET` (at least 32 characters)
- `JANAVANI_IDENTITY_ASSERTION_SECRET` (at least 32 characters)
- `JANAVANI_IDENTITY_ASSERTION_ISSUER`
- `JANAVANI_IDENTITY_ASSERTION_AUDIENCE`
- `JANAVANI_WEB_API_URL` (HTTPS in production)

These must be configured for the actual selected OIDC provider and API trust relationship. Do not paste secrets into GitHub, client JavaScript, URLs, tickets, or chat. Optional OIDC failure must not make anonymous drafting unavailable.

Before enabling persistent production accounts, verify the canonical Postgres schema and migrations, identity-link provider selection, webhook inbox DSN and encryption-key rotation, session expiry/revocation, account recovery, authorization tests, and live end-to-end tests across the WebApp and Telegram bot. Never switch production traffic to an in-memory fallback simply to make a health check pass.

## Secret handling

Secrets belong in the hosting provider's secret manager or environment configuration. The populated `.env` must remain outside the repository. Secrets must not be embedded in source code, client bundles, logs, telemetry, crash reports, public repositories, or screenshots.

## Implementation status summary

- Anonymous drafting path: **IMPLEMENTED ON FEATURE BRANCH; TESTS RUNNING**
- OIDC client/session safeguards: **CODE AND TESTS PRESENT; PROVIDER/PRODUCTION VERIFICATION REQUIRED**
- Telegram account opt-in: **IMPLEMENTED ON FEATURE BRANCH; REQUIRES SHARED POSTGRES CONFIGURATION**
- Web↔Telegram pairing: **CODE PRESENT; LIVE CROSS-SURFACE CONFIGURATION NOT VERIFIED**
- Email OTP: **NOT IMPLEMENTED**
- Mobile/SMS OTP: **NOT IMPLEMENTED**
- Generated key-pair/passkey account: **NOT IMPLEMENTED**
- Secure encrypted Telegram webhook on Railway: **BLOCKED ON REQUIRED DURABLE STORAGE CONFIGURATION**
- Production deployment and security verification: **NOT COMPLETE**

## Related canonical documents

- `docs/SOURCE_OF_TRUTH.md`
- `docs/IDENTITY_ACCESS_TRUST.md`
- `docs/PRIVACY_ARCHITECTURE.md`
- `docs/architecture/web-telegram-identity-pairing.md`
- `SECURITY.md`

**Rule: Do not describe Janavani as having complete production authentication until each advertised method, recovery path, authorization gate, deployment, test suite, and security review has passed.**
