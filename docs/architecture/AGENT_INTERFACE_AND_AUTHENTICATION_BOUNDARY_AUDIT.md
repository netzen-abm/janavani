# Agent Interface and Authentication Boundary Audit

## Status

Audit evidence and migration boundary. This document does not remove the remaining agent API.

## Verified main baseline

Main: `a0043afccbb1cf243e4b07dcf55083cdf6d4fb55`

The dedicated legacy SOS reverse-proxy route has been removed. The canonical SOS route is `POST /api/v1/sos/trigger`.

## Findings

### 1. The `/api/v1/agent/` namespace is still active

The broader nginx location remains because active repository consumers still use agent paths for document drafting/retrieval and telemetry.

Observed current consumers include:

- `src/adapters/web_client.py` → `/api/v1/agent/draft`
- `src/adapters/telegram_client.py` → `/api/v1/agent/draft` and `/api/v1/agent/retrieve/{tracking_id}`
- deployment health checks → `/api/v1/agent/metrics`
- Prometheus configuration → `/api/v1/agent/metrics`
- internal admin dashboard → `/api/v1/agent/metrics`

Therefore removing the entire nginx `/api/v1/agent/` proxy would be premature.

### 2. The old SOS route is no longer an active canonical route

The old `POST /api/v1/agent/trigger-sos` was removed from nginx because the canonical application mounts `src.web.sos_router` with `POST /api/v1/sos/trigger`.

Historical documentation may still mention the old route and must be treated as historical until reconciled.

### 3. Interface tokens remain a live service-to-service credential mechanism

The current repository still uses:

- `JANAVANI_INTERFACE_TOKENS`
- `WEB_INTERFACE_TOKEN`
- `ADMIN_INTERFACE_SECRET_TOKEN`
- `X-Janavani-Interface-Token`

for selected internal/server-side paths.

This is distinct from the legacy SOS blacklist mechanism. The audit found no current canonical consumer of `security:blacklisted_tokens:*`.

The correct conclusion is therefore **not** to remove interface tokens globally. They are still used by active adapters and internal endpoints.

### 4. Canonical citizen identity and service credentials are separate

The canonical SOS path uses the verified identity assertion boundary and produces `IdentityContext`.

Interface tokens are service credentials used by server-side/internal integrations. They must not become citizen identity.

### 5. Remaining convergence gap

The repository still contains multiple generations of agent/draft infrastructure and historical v2/v3 implementations.

The next convergence task should be to identify the exact active owner for:

- `/api/v1/agent/draft`
- `/api/v1/agent/retrieve/{tracking_id}`
- `/api/v1/agent/metrics`

and then migrate each capability independently toward canonical capability contracts.

Do not replace all three with one generic "agent" capability.

## Disposition

| Area | Classification | Action |
|---|---|---|
| `/api/v1/sos/trigger` | Canonical | Keep |
| `/api/v1/agent/trigger-sos` | Legacy | Removed from nginx |
| `/api/v1/agent/draft` | Transitional/active | Preserve until canonical draft owner is verified |
| `/api/v1/agent/retrieve/{tracking_id}` | Transitional/active | Preserve until transient-document owner is verified |
| `/api/v1/agent/metrics` | Transitional/active | Preserve until telemetry owner is verified |
| `X-Janavani-Interface-Token` | Active service credential mechanism | Do not remove globally |
| `security:blacklisted_tokens:*` | Legacy/unverified consumer | Do not recreate; verify no live dependency before deleting legacy engine |
| Nostr emergency construction | Legacy | Do not revive; only implement behind canonical delivery boundary if separately approved |

## Next architectural move

The highest-value next step is **capability-by-capability agent API convergence**, starting with `/draft`, because it is directly used by active Web and Telegram adapters and is already documented as having multiple generations.

This should be a bounded migration of one capability, not a wholesale agent rewrite.
