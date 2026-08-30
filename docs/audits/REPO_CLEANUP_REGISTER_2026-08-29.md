# Repository Cleanup Register — 2026-08-29

## Scope

This register records cleanup actions and evidence-backed findings. It is intentionally conservative: functional/legacy code or configuration is not deleted merely because another implementation exists.

## Confirmed empty placeholders removed

The following files were verified as newline-only files and removed from the Case capability convergence branch:

- `src/services/ai_service.py`
- `src/services/classification_service.py`
- `src/services/complaint_service.py`

All three previously contained no executable implementation.

## Configuration-generation findings — 2026-08-30

### `nginx.conf`

**Classification: INVESTIGATE → likely CONVERGE/ARCHIVE**

Direct evidence on `cleanup/github-actions`:

- contains two `events {}` blocks;
- contains two `http {}` blocks;
- contains two server definitions for the same internal host;
- contains duplicated proxy/rate-limit configuration;
- routes to `ai-agent-service:8000`;
- current `docker-compose.yml` defines `janavani-api` as the application service instead;
- current Dockerfile starts `src.web.canonical_app:app`;
- canonical application assembly is FastAPI and registers current capability routers.

This is strong evidence of generational configuration drift, but the file is not deleted yet because historical deployment intent may still be useful for reconstruction.

### `docker-compose.yml`

**Classification: KEEP / CONVERGE**

The application service currently launches the canonical FastAPI application. The Redis service is explicitly configured as transient memory infrastructure. However, service naming and reverse-proxy configuration should be reconciled so all deployment layers describe the same runtime architecture.

## Cleanup policy

1. Confirm file content and consumers.
2. Classify as empty placeholder, duplicate, legacy, canonical, experimental, or configuration drift.
3. Remove only confirmed-obsolete material when no runtime/deployment consumer requires it.
4. For duplicate or legacy implementations/configuration: archive/isolate first where practical.
5. Run tests/CI after cleanup.
6. Never equate absence of search results with proof that a file has no runtime consumer.

## Next cleanup targets

- Enumerate all zero-byte/newline-only files.
- Identify duplicate capability implementations.
- Map every runtime entrypoint and deployment workflow to its owner.
- Audit Docker, Compose, Nginx, environment templates, and CI as one configuration surface.
- Consolidate shared infrastructure under provider-neutral contracts.
- Keep Telegram/Web/mobile as independent adapters over shared capabilities.
- Establish one canonical production reverse-proxy configuration before removing the generational Nginx configuration.
