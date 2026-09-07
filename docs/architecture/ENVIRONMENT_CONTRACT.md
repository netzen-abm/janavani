# Environment Contract

## Purpose

This document is the canonical environment-variable contract for Janavani deployments.
Configuration belongs to the runtime environment; capability code must consume configuration rather than own credentials.

## Service boundary rule

Janavani uses independent runtime surfaces. A credential is configured only on the service that actually needs it.

**Do not copy every secret into every Render service.** Apply least privilege.

In particular:

- The canonical Web/API service does **not** need `TELEGRAM_BOT_TOKEN` merely because Janavani supports Telegram.
- The independent Telegram runtime receives `TELEGRAM_BOT_TOKEN`.
- AI provider credentials belong only to the runtime that directly invokes the corresponding provider.
- Database and artifact-storage credentials belong to the canonical persistence runtime that uses them.
- Interface tokens are service-to-service credentials, not citizen identity credentials.
- `JANAVANI_IDENTITY_ASSERTION_SECRET` is a service-to-service trust credential for the temporary signed-assertion gateway boundary; it is **not** a citizen credential and must never be exposed to browsers, Telegram clients, or other untrusted interfaces.

## Canonical provider credentials

Use these names consistently across code, CI, and deployment:

- `OPENROUTER_API_KEY` — OpenRouter AI provider credential.
- `HF_TOKEN` — Hugging Face provider credential.
- `SUPABASE_URL` — Supabase integration configuration.
- `SUPABASE_ANON_KEY` — Supabase integration access credential.
- `TELEGRAM_BOT_TOKEN` — Telegram bot integration credential; **not** a citizen-login credential.
- `JANAVANI_POSTGRES_DSN` — PostgreSQL connection credential/configuration for production persistence.
- `JANAVANI_ARTIFACT_S3_BUCKET` — S3-compatible artifact bucket name.
- `JANAVANI_ARTIFACT_S3_ENDPOINT_URL` — optional S3-compatible endpoint override.
- `JANAVANI_ARTIFACT_S3_PREFIX` — optional artifact key prefix; defaults to `artifacts`.

`HF_TOKEN` is the canonical Hugging Face credential name.
Do not introduce `HUGGINGFACE_API_KEY` as an alternate name.

## Canonical runtime configuration

Production persistence is fail-closed and requires:

- `JANAVANI_RUNTIME_MODE=production`
- `JANAVANI_CASE_REPOSITORY_PROVIDER=postgres`
- `JANAVANI_ARTIFACT_REPOSITORY_PROVIDER=postgres`
- `JANAVANI_EVIDENCE_REPOSITORY_PROVIDER=postgres`
- `JANAVANI_ARTIFACT_BLOB_PROVIDER=s3`
- `JANAVANI_POSTGRES_DSN=<secret connection string>`
- `JANAVANI_ARTIFACT_S3_BUCKET=<bucket name>`

These are application configuration values except the DSN, which must be treated as a secret.

## Canonical interface credentials

Configure only where the corresponding interface or internal service is enabled:

- `WEB_INTERFACE_TOKEN` — server-side Web/API interface credential where required.
- `JANAVANI_INTERFACE_TOKENS` — configured interface-token set for protected API endpoints.
- `ADMIN_INTERFACE_SECRET_TOKEN` — internal admin interface credential.
- `JANAVANI_IDENTITY_ASSERTION_SECRET` — temporary trusted-gateway signing secret used by the Web/API identity assertion verifier. This must be generated and stored only in the server-side secret store.

These values must never be hard-coded, committed, or reused as citizen identity.

## Service matrix

| Variable | Web/API | Telegram | AI runtime | Admin | CI/test | Classification |
|---|---:|---:|---:|---:|---:|---|
| `JANAVANI_RUNTIME_MODE` | Yes | If production | If production | If separate | Fixture | Runtime config |
| `JANAVANI_CASE_REPOSITORY_PROVIDER` | Yes | If directly persists cases | No | No | Fixture | Provider selection |
| `JANAVANI_ARTIFACT_REPOSITORY_PROVIDER` | Yes | If directly persists artifacts | No | No | Fixture | Provider selection |
| `JANAVANI_EVIDENCE_REPOSITORY_PROVIDER` | Yes | If directly persists evidence | No | No | Fixture | Provider selection |
| `JANAVANI_ARTIFACT_BLOB_PROVIDER` | Yes | If directly stores artifacts | No | No | Fixture | Provider selection |
| `JANAVANI_POSTGRES_DSN` | Yes | Only if directly using DB | No | No | `JANAVANI_POSTGRES_TEST_DSN` for integration tests | Secret |
| `JANAVANI_ARTIFACT_S3_BUCKET` | Yes | Only if directly storing blobs | No | No | Fixture | Storage config |
| `JANAVANI_ARTIFACT_S3_ENDPOINT_URL` | If non-default S3 | If needed | No | No | Optional | Storage config |
| `JANAVANI_ARTIFACT_S3_PREFIX` | Optional | Optional | No | No | Optional | Storage config |
| `OPENROUTER_API_KEY` | Only if API invokes AI | No | Yes | No | Mock fixture | Secret |
| `HF_TOKEN` | Only if API invokes HF | No | Yes | No | Mock fixture | Secret |
| `SUPABASE_URL` | If integration is used | If integration is used | No | If integration is used | Fixture | Integration config |
| `SUPABASE_ANON_KEY` | If integration is used | If integration is used | No | If integration is used | Fixture | Secret |
| `TELEGRAM_BOT_TOKEN` | **No by default** | **Yes** | No | No | Mock/secret in bot CI | Secret |
| `WEB_INTERFACE_TOKEN` | If protected server adapter/health check is enabled | No | If calling Web/API | No | Fixture | Service credential |
| `JANAVANI_INTERFACE_TOKENS` | If protected API endpoints are enabled | If interface calls them | If interface calls them | No | Fixture | Service credential |
| `ADMIN_INTERFACE_SECRET_TOKEN` | No | No | No | Yes | Fixture | Service credential |
| `JANAVANI_IDENTITY_ASSERTION_SECRET` | If Web/API identity gateway is enabled | No | No | No | Test-only fixture | Service trust secret |
| `JANAVANI_AI_BASE_URL` | If server-side AI adapter is used | No | Yes | No | Fixture | Non-secret URL |
| `JANAVANI_INTERNAL_API_URL` | No | No | No | Yes | Fixture | Internal URL |
| `JANAVANI_INTERNAL_FEEDBACK_URL` | No | No | No | Yes | Fixture | Internal URL |
| `REDIS_HOST` / `REDIS_PORT` | If Redis capability is enabled | If needed | If needed | If needed | Fixture | Runtime infrastructure |
| `JANAVANI_ARTIFACT_BLOB_ROOT` | Development/local only | Development/local only | No | No | Fixture | Local storage |
| `JANAVANI_POSTGRES_TEST_DSN` | No | No | No | No | Integration tests | Test-only secret |

The matrix describes intended ownership. A service should not receive a variable merely because another service uses it.

## Development/test rules

Tests use non-secret fixture values. Test credentials must never be copied from production.

`JANAVANI_POSTGRES_TEST_DSN` is reserved for external PostgreSQL integration tests.

Local development may use the local artifact provider and local Redis defaults where supported.

## Production secret rules

Production credentials remain in the deployment platform's secret/environment store.

Never commit populated `.env` files, provider tokens, database passwords, private keys, or service credentials.

Never place real credentials in documentation, screenshots, test fixtures, source code, or commit messages.

If a credential is exposed, rotate it rather than merely deleting it from the latest source revision.

## Capability rule

Provider credentials belong to the runtime environment.
Capability code must consume configuration, not own credentials.

A provider credential authorizes access to a provider; it does not authorize a citizen action. Citizen identity, capability authorization, consent, and consequential-action approval remain separate concerns.
