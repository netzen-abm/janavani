# Janavani WebApp on Vercel Hobby

## Deployment boundary

The WebApp is an independent FastHTML/Starlette surface rooted at `src/webapp`. It calls the canonical FastAPI API through `JANAVANI_WEB_API_URL`; it does not own Case persistence, consent state, authority truth, or document-rendering logic. The API remains rooted at `src.web.canonical_app:app`.

Configure the separate Vercel project with:

- Repository: `netzen-abm/janavani`
- Root Directory: `src/webapp`
- Framework preset: `FastAPI` (the entrypoint is an explicit FastAPI ASGI wrapper around the existing FastHTML app).
- Enable source files outside the root directory, because the entrypoint imports the repository's `src/` package tree.
- Keep Preview deployments and Production environments separate. Do not copy Telegram credentials into this project.
- Use `requirements.txt` only for the WebApp runtime; use root `requirements-api.txt` for the canonical API project.

## Required production environment

Do not set `JANAVANI_RUNTIME_MODE=production` until the API's durable providers and secrets have been verified. Production sign-in requires:

- `JANAVANI_RUNTIME_MODE=production`
- `JANAVANI_WEB_API_URL`: HTTPS URL of the canonical API
- `JANAVANI_WEB_SESSION_SECRET`: independently generated secret with at least 32 characters
- `JANAVANI_IDENTITY_ASSERTION_SECRET`: at least 32 characters; must match the API verifier's secret
- `JANAVANI_IDENTITY_ASSERTION_ISSUER` and `JANAVANI_IDENTITY_ASSERTION_AUDIENCE`: exactly match API trust configuration
- `JANAVANI_OIDC_ISSUER_URL`, `JANAVANI_OIDC_CLIENT_ID`, `JANAVANI_OIDC_CLIENT_SECRET`, and `JANAVANI_OIDC_REDIRECT_URI`: values from the selected OIDC provider, with the callback registered exactly.

Generate secrets in an approved secret manager and enter them through Vercel's encrypted environment-variable interface. Never commit values or share them between Preview and Production unless there is an explicit security decision.

## Release checks

1. Verify the Vercel deployment build and inspect the bundled dependencies.
2. Check `/` and `/liveness`; verify `/auth/login` redirects to the configured OIDC issuer when valid credentials are present.
3. Complete OIDC login/callback/logout, including state, nonce, PKCE, Secure/HttpOnly/SameSite cookie checks and cross-origin mutation rejection.
4. Create a Case, list only Cases owned by that authenticated principal, review it, record explicit consent, and download a PDF/DOCX artifact. Confirm nothing is automatically emailed or submitted.
5. Repeat after a service restart and from a second identity. A different citizen must never see another citizen's records.

## Known release blockers

The current Janavani Supabase project is inactive and its database connection has timed out; the current Vercel project has no API persistence/OIDC environment configured. The 30-minute signed session cookie is stateless, so clearing it at logout cannot revoke a copied cookie server-side. Do not use this deployment for sensitive, persistent citizen records until a revocation-capable session policy and durable provider configuration are verified.

Vercel Hobby has recently rate-limited this repo's builds. Batch related changes into one commit and validate GitHub CI before requesting a preview build. Do not work around provider limits or promote a preview solely because it is marked Ready.
