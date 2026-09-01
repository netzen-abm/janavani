# Janavani GitHub Workflow Archive Manifest

These workflows are historical, generic, redundant, invalid, or superseded automation paths. Their contents are preserved here under the archive-first rule before removal from the active execution surface.

## Archived in this convergence pass

- `django.yml` — generic Django CI; no `manage.py` entrypoint exists in the repository.
- `docker-image.yml` — redundant generic Docker build; container publishing has its own workflow.
- `greetings.yml` — generic greeting template; no Janavani capability.
- `jekyll-docker.yml` — generic Jekyll build; not the active Janavani web stack.
- `manual.yml` — generic greeting workflow; no Janavani capability.
- `stale.yml` — generic issue-management template; not part of the canonical governance/CI control plane.
- `python-app.yml` — generic Python starter workflow superseded by canonical CI.
- `python-package.yml` — generic package starter workflow superseded by canonical CI.
- `verify-crate.yml` — empty workflow placeholder.
- `ai-test-compliance.yml` — invokes a missing `ai_pipeline.py` entrypoint and is not aligned with the active AI capability adapter architecture.
- `startup-check.yml` — imports legacy Flask-oriented modules and is superseded by canonical FastAPI/runtime validation.
- `python-publish.yml` — generic PyPI starter workflow; current `pyproject.toml` is Vercel configuration rather than a Python package build manifest.
- `python-package-conda.yml` — obsolete Conda starter workflow; `environment.yml` is absent.

## Retained active classes

Canonical CI, security/compliance validation, dependency review, Docker publishing, decentralized verification, AI capability validation where backed by current entrypoints, and real deployment workflows remain active until individually verified.

## Rule

Do not delete archived material merely to make search results cleaner. Historical material is evidence. Active automation must be capability-owned, executable against the current repository, and non-duplicative.
