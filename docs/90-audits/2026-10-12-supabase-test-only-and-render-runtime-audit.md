# Supabase Test-Only and Render Runtime Audit

**Date:** 12 October 2026  
**Status:** Decision recorded; dashboard/runtime verification remains open  
**Scope:** Janavani repository, Render configuration, and operator-provided Render dashboard screenshots.

## Decision

Supabase is for testing only and uses the free tier. It is **not** the production persistence decision. Do not make Supabase the canonical production database, add a production dependency on it, or create a second production database merely because SUPABASE_URL and SUPABASE_ANON_KEY are visible in a Render environment screen.

The repository's current master checklist records PostgreSQL as the canonical relational standard and says the active Supabase runtime/build dependency was removed on 19 September 2026. Preserve that boundary unless a later, explicit architecture decision supersedes it.

## Evidence reviewed

- render.yaml on main declares janavani-web-api as a Python web service and janavani-telegram as an independent worker. The worker receives TELEGRAM_BOT_TOKEN through a non-synchronized secret.
- The Render dashboard screenshot shows a live Web service named JanaVani, connected to netzen-abm/janavani, branch main, with a live status and environment-variable names SUPABASE_URL, SUPABASE_ANON_KEY, and TELEGRAM_BOT_TOKEN.
- The screenshot masks values; no secret values were accessed or recorded.
- The master checklist states that Supabase is not required by the active runtime/build/startup configuration and that PostgreSQL is the relational standard.
- The repository declares a separate Telegram worker in render.yaml, but a Blueprint declaration does not prove that the worker has been provisioned, deployed, healthy, or correctly configured in the Render dashboard.

## Required reconciliation

1. Inspect the current application code and deployment configuration before changing dashboard variables. Confirm no active production code imports or requires Supabase.
2. In Render, inspect whether SUPABASE_URL and SUPABASE_ANON_KEY are genuinely unused by the main Web service. If confirmed unused, remove them from the production service to reduce configuration drift. Do not remove them from a separate test environment that still needs them.
3. Never paste secrets into GitHub, logs, issues, this document, or chat. Rotate a secret only if exposure is suspected; do not rotate secrets simply because their names are visible.
4. Verify whether the janavani-telegram worker exists in Render and is healthy. If absent, reconcile it from the Blueprint only after checking the service plan and required variables. Do not assume it is deployed because render.yaml declares it.
5. Confirm both surfaces use the intended canonical application persistence and identity provider. Shared environment-variable names alone are not proof of shared durable state.
6. Keep production persistence selection explicit: provider contract, migrations, least-privilege runtime role, cross-user authorization, transaction/concurrency tests, restart recovery, and backup/restore evidence must pass before production data is enabled.

## Cost and architecture recommendation

Do not provision another database or adopt paid infrastructure during this audit. First verify the current implementation and free-tier constraints. A free testing database can support development and disposable integration tests, but should not be represented as production-ready durable infrastructure without evidence for availability, retention, backups, capacity, and recovery.

Keep the application persistence boundary provider-neutral only where that boundary already exists and is useful. Do not introduce a new universal storage abstraction solely to accommodate a test-only provider. Keep domain lifecycle invariants together; separate Web and Telegram adapters and independently deployed runtimes where they create real trust, transport, or failure boundaries.

## Release gate

Production citizen Case/evidence/submission data remains blocked until the chosen production provider is explicitly configured and verified. The WebApp and Telegram bot must not claim cross-surface continuity unless they resolve the same authorized identity and canonical records through that provider.

## Next two actions

1. Reconcile Render environment variables against actual active code and confirm the Telegram worker's real deployment state.
2. Complete the canonical Web–Telegram civic-action journey against the selected persistence provider, including authorization isolation, idempotency, restart recovery, and operational evidence.
