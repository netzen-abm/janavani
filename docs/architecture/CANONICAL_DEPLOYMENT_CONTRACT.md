# Janavani Canonical Deployment Contract

**Status:** Proposed canonical baseline  
**Purpose:** Prevent Docker, Compose, reverse-proxy, CI, and application layers from drifting into different architectural generations.

## Canonical runtime

The application runtime is the FastAPI assembly exposed by:

`src.web.canonical_app:app`

The deployment service name used by Compose is:

`janavani-api`

The application listens on container port `8000`.

## Runtime flow

```text
Internet
  ↓
Reverse proxy / TLS boundary
  ↓
janavani-api:8000
  ↓
src.web.canonical_app:app
  ↓
Shared capability/domain services
```

## Service ownership

| Layer | Canonical responsibility |
|---|---|
| Dockerfile | Build and start the canonical application runtime |
| Docker Compose | Local/deployment service topology |
| Nginx | Public reverse proxy and TLS boundary |
| FastAPI | HTTP/API application assembly |
| Domain/services | Shared business capabilities |
| Access surfaces | Web, Telegram, API and future clients consume shared capabilities |

## Redis

Redis is infrastructure, not business logic. It may be used for transient/cache/rate-limit concerns and must not become an alternative source of truth for canonical case state.

## Reverse-proxy contract

The canonical reverse proxy must:

1. terminate TLS where TLS is owned by the deployment boundary;
2. forward application traffic to `janavani-api:8000`;
3. not reference an unregistered service such as `ai-agent-service` unless that service is explicitly restored to the canonical architecture;
4. contain exactly one top-level Nginx `events` block and one top-level `http` block;
5. define intentional rate limits once per applicable policy;
6. preserve forwarding headers required by the application;
7. avoid duplicating competing server definitions for the same deployment target.

## Health and verification

Before replacing generational reverse-proxy configuration, verify at minimum:

- container starts successfully;
- `src.web.canonical_app:app` imports successfully;
- application port `8000` is reachable inside the deployment network;
- Compose service name resolves from the reverse-proxy container;
- expected API routes respond;
- reverse proxy can reach the application;
- TLS configuration is syntactically valid when enabled.

## Configuration-generation rule

Dockerfile, Compose, Nginx, environment templates, CI/CD workflows, and application entrypoints are one deployment configuration surface. A configuration artifact is not canonical merely because it is syntactically valid or production-looking.

Any mismatch between these layers must be recorded as `INVESTIGATE` until runtime evidence establishes the correct generation.

## Change-control rule

Do not delete the historical `nginx.conf` until a canonical replacement has been created, validated, and its provenance is recorded in the cleanup register.
