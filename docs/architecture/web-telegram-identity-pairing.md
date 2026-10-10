# Web–Telegram Identity Pairing

## Contract

Pairing links a Telegram provider subject to an existing canonical Janavani principal. It does not make Telegram's numeric user ID the canonical principal and does not grant authority to read arbitrary cases.

1. An authenticated Web session requests a challenge.
2. Janavani returns a high-entropy, five-minute code with `Cache-Control: no-store`.
3. The citizen sends `/pair CODE` to Janavani in a private Telegram chat.
4. Telegram claims the code; this is not yet a verified link.
5. The same authenticated Web principal explicitly confirms the pending pairing.
6. The PostgreSQL transaction creates the verified identity link and marks the challenge confirmed atomically.

Codes are stored only as SHA-256 digests. Claims and confirmations are single-use. Expired, mismatched-principal and conflicting identity links fail closed. Telegram attempts to delete the submitted command message, but this is best-effort and cannot erase notifications, client caches or external logs.

## Shared-process requirement

The Web API and Telegram bot are independent processes. In-memory pairing is therefore not a valid cross-surface deployment. The Web pairing API returns HTTP 503 and the bot reports pairing unavailable unless the shared provider is selected.

Configure both services consistently:

- `JANAVANI_EXTERNAL_IDENTITY_LINKS_REPOSITORY_PROVIDER=postgres`
- `JANAVANI_RUNTIME_MODE=production`
- `JANAVANI_IDENTITY_LINKS_DSN` pointing to the same identity database/schema on both services
- `JANAVANI_IDENTITY_ASSERTION_SECRET`, issuer and audience on the Web API, supplied only by the trusted identity gateway contract

Use a dedicated least-privilege database role and secret manager. Do not place database DSNs or the assertion secret in frontend JavaScript, a Telegram client, or a committed environment file. Never enable the pairing capability on one surface only and assume it will work across processes.

## API

- `POST /civic/identity-pairings` — authenticated challenge issuance.
- `POST /civic/identity-pairings/{pairing_id}/confirm` — authenticated confirmation with `{"explicit_confirmation": true}`.

The endpoint confirms an identity link; it does not, by itself, establish that every existing Case query correctly enforces ownership. Each protected resource must continue to authorize the canonical principal independently.

## Release gates

Do not treat this as production-ready until all are demonstrated:

- Migration applied to a clean PostgreSQL database.
- Web and Telegram point to the same database and schema.
- Concurrent claim/confirm tests prove single-use behavior under races.
- Conflicting identity links cannot be reassigned.
- Integration tests prove link resolution from a second process after confirmation.
- Rate limiting, monitoring and challenge cleanup/retention are configured.
- Web auth gateway assertions are short-lived, signed, audience/issuer checked and never browser-controlled.
- CI, CodeQL and deployment checks are green; a failed AI review caused by quota exhaustion is inconclusive.

## Ownership boundaries

- `src/identity/pairing.py`: state machine, code generation, expiry and confirmation invariants.
- `src/storage/repositories/postgres_identity_pairing.py`: PostgreSQL locking and atomic persistence.
- `src/web/identity_pairing_router.py`: authenticated HTTP adapter.
- `src/commands/pair.py`: private-chat Telegram adapter.
- `src/platform/composition_repositories.py`: provider selection.

Do not create separate layers unless a new trust boundary, persistence provider or independently reused behavior justifies them.
