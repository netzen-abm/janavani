# Archived GitHub Actions — 2026-09-01

These workflows were removed from active execution because they are generic starter templates, duplicate an existing canonical gate, target an obsolete technology, are unconfigured deployment templates, or do not provide a real Janavani capability.

Archive-first rule: historical workflow material is preserved here before active removal.

Active canonical workflow set after this cleanup:
- `ci.yml` — canonical Python/runtime test gate
- `security-ci.yml` — secret/privacy and component verification
- `dependency-review.yml` — dependency vulnerability review on PRs
- `label.yml` — PR path labeling
- `docker-publish.yml` — canonical container build/publish/signing
- `verify-decentralized-stack.yml` — independent Rust protocol verification

Archived classifications:
- obsolete application/template workflows: Django, Jekyll, generic Python, greetings, manual, stale
- duplicate/redundant checks: generic Docker build, pip-only check, Pylint, Codacy, Hadolint
- unconfigured deployment templates: Octopus Deploy, OpenShift
- unready decentralized deployment: Freenet deployment placeholder
- invalid/generic provenance template: generic SLSA generator
- obsolete AI/issue automation: AI compliance runner, issue summarizer
- empty workflow: verify-crate
- obsolete Python package publishing: python-publish

If a future capability becomes real, create a capability-specific workflow from the canonical architecture rather than restoring these templates unchanged.
