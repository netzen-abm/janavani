# Janavani — Engineering Proof Cycle Checkpoint
**Date:** 2026-10-27  
**Purpose:** Record the verified state and define the next smallest code/verification cycle without introducing another architecture generation.

## Decision

The current cycle remains a proof cycle. Prioritize a working citizen journey across the existing canonical capability boundaries and prove WebApp/Telegram independence. Do not add generalized abstractions unless a testable defect demonstrates the need for a separate change, trust, persistence, provider, deployment, or reuse boundary.

## Live repository state checked

- Repository: `netzen-abm/janavani`
- Default branch: `main`
- Main SHA checked: `ff3600670065bd5af6008a6edaab22bf20fb9392`
- Branch inventory observed: exactly eight refs, matching the eight approved roles in `docs/BRANCH_GOVERNANCE.md`.
- `main` commit statuses include successful Vercel website/WebApp and Railway Telegram deployment checks.
- `main` aggregate CI and Branch Retirement workflow reported failure. The Python test job itself passed, including the Web vertical-slice tests, Web/Telegram shared-capability gate, canonical test suite, live PostgreSQL RLS gate, backup/restore check, and PostgreSQL restart durability check. Governance failures must still be diagnosed and resolved before calling repository CI green.
- PR #203 (`integration/canonical-platform`) remains open and unmerged; GitHub currently marks it non-mergeable/dirty. It is 50 commits ahead and 1,922 behind `main`, with 59 changed files. Do not merge wholesale. Reconcile its unique useful changes selectively against current `main`.
- The latest status observed for PR #203's head SHA `9668bc47ef3d2758d67d3530bd92d0ad15b5bb4c` reports failed Vercel build-rate-limit / Netlify preview statuses. The head is behind current main and those statuses are not proof of current-main failure.
- Branch `chore/ecosystem-shared-capability-infrastructure` has successful Vercel and Netlify preview statuses. Its branch delta is 638 commits ahead / 3 behind main across 208 files; it needs careful PR-level diff review, not a blanket merge.

## Existing canonical implementation to reuse

- `src/capabilities/civic_case.py` owns canonical Case capability semantics.
- `src/capabilities/civic_action_capability.py` composes an owned Case, verified Authority and a reviewable document draft; its artifact-generation path intentionally has no submission transport.
- `src/capabilities/letter_drafting.py` composes structured civic letters through existing Case and DocumentReview capabilities.
- `src/platform/surface_case_composition.py` composes shared capabilities for Web/Telegram surfaces; it should remain the shared composition boundary.
- `src/web/canonical_app.py` is the canonical FastAPI app.
- `src/webapp/main.py` and `src/webapp/case_workspace.py` provide the interactive browser surface and review/consent/artifact routes.
- `tests/test_web_telegram_shared_case_contract.py` checks common capability use and ownership-scoped access. It does not by itself prove that two live deployments use the same durable database, identity mapping or continuity policy.
- `render.yaml` currently starts Telegram with `python src/bot_telegram.py`; that script's `main()` uses `application.run_polling()`. Polling is not to be used for the requested deployment cycle.

## Letter drafting — next product-level improvement

Do not create another draft engine or copy templates into channel handlers. Extend the existing canonical letter/document capability only after checking its model and tests.

Implement or verify a privacy-safe reusable template model with:
- template key/version, language, civic action type, required/optional fields and document structure;
- no citizen-provided values, identity details, contact data, case narrative, evidence bytes, credentials or other personal/sensitive data in saved templates;
- user-reviewable draft generation from a selected template, with AI assistance offered as a user choice and a deterministic template path always available;
- AI output clearly marked as generated, never treated as authoritative law/fact; source/citation and uncertainty markers retained where relevant;
- distinct states for draft, reviewed, user-approved-for-download, and externally submitted. Draft generation must not send/email/submit a document;
- templates versioned and reused on a similar use case; improve a prior template only through an explicit/versioned change, not by storing a citizen's personal draft as a model.
- regression tests for privacy stripping, template reuse, deterministic fallback, AI failure, malformed/unsupported claims, and no implicit submission.

First inspect existing template/document models, registries and tests. Reuse them if they already meet these requirements; only create a new file if inventory proves no appropriate owner exists.

## Telegram webhook — hard gate

- Do not use `run_polling()` for deployment.
- Do not switch the Render service to an imagined or unverified webhook entrypoint.
- Inspect existing Telegram webhook/router support, provider signature/secret validation, deduplication/replay control, bounded payloads, response timing, and current deployment startup.
- The webhook should translate updates and dispatch to the existing shared capability graph, not duplicate Case, Authority, Evidence, Consent or Document logic.
- Telegram service must own its webhook runtime and failure domain; WebApp must remain operational if Telegram is down and vice versa.
- Verify how a citizen identity is securely bound between Telegram and WebApp before claiming that the same private Case can be continued across surfaces. A Telegram user ID alone must not silently become a verified Janavani identity.
- Add runtime/E2E tests for valid/invalid webhook secret, duplicate update, non-message update, dispatch/provider failure, shared capability invocation and isolated surface failure. Do not claim production readiness without deployment evidence.

## Next execution order

1. Diagnose the latest `main` CI branch-budget failure and branch-retirement failure; preserve archive-before-delete behavior and re-check the eight physical refs.
2. Review the exact existing document template/model ownership and tests, then make the smallest change for privacy-safe template reuse if a verified gap exists.
3. Implement/verify Telegram webhook entrypoint against existing adapters; change deployment only after tests establish correct startup and request handling.
4. Execute WebApp + Telegram acceptance path against the same selected persistence provider: create Case → retrieve after process restart → verify owner-only access → prepare/reuse letter template → user edits/reviews → explicit consent for chosen operation → download; no submission unless a separately approved submission capability is implemented.
5. Re-run CI and obtain runtime evidence; keep PR #203 on hold until its unique delta is reconciled and gates pass.

## Completion language

Use only evidence-backed states: designed, implemented, unit-tested, integration-tested, deployment-verified, privacy/security-verified, production-ready. Passing CI alone is not production certification.

## Status

- **Done:** live repository/branch/PR/check status rechecked; existing Case/document/letter/template-related code located; no-polling requirement and verification gates recorded.
- **In progress:** branch-governance failure diagnosis; letter-template model/test audit; webhook support and deployment entrypoint audit.
- **Next two steps:** resolve the branch-budget/retirement CI failure with archive-first controls; then audit existing letter-template models/tests before any draft-engine changes.
