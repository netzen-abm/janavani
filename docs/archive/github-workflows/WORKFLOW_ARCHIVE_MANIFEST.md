# Janavani GitHub Workflow Archive Manifest

These workflows were removed from the active `.github/workflows/` execution surface because they are generic starter workflows, obsolete deployment templates, or redundant validation paths. Their contents are preserved here under the archive-first repository rule.

## Archived in this convergence pass

- `django.yml` — generic Django CI; repository has no `manage.py` entrypoint.
- `jekyll-docker.yml` — generic Jekyll site build; Janavani's active web stack is not Jekyll.
- `manual.yml` — generic greeting workflow; no Janavani capability.
- `pylint.yml` — broad legacy lint workflow superseded by canonical validation boundaries.
- `python-app.yml` — generic Python starter workflow superseded by canonical CI.
- `python-package.yml` — generic package starter workflow superseded by canonical CI.
- `python-package-conda.yml` — generic Conda workflow with no active Conda environment contract.
- `docker-image.yml` — redundant generic Docker build; container publishing has its own workflow.

## Explicitly retained

Deployment, security, decentralized-integration, AI-compliance, dependency-review, and other workflows remain active until their capability ownership and operational role are verified.

## Rule

Do not delete archived material merely to make repository search cleaner. Historical references remain valid archive evidence. Active execution surfaces must be canonical, intentional, and capability-owned.
