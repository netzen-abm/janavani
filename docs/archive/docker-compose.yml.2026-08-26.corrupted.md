# Archived Docker Compose corruption record

**Archived:** 2026-08-26
**Original path:** `docker-compose.yml`
**Original blob SHA:** `bf88b1e40f6237a702ce6d558d23789d9bbc836c`
**Source commit/ref:** `refactor/document-capability-convergence`

## Reason for archival

The file contained multiple concatenated Compose generations in one YAML document. CI failed before service startup because YAML mapping keys such as `version`, `services`, and `networks` were repeatedly redefined. This is a confirmed multi-generational/overwritten configuration defect, not an optional feature failure.

The exact historical file remains recoverable from Git history using the original blob SHA above. This archive record is retained before replacement in accordance with the repository rule: **archive first; delete only after evidence**.

## Evidence

GitHub Actions run `32941882219`, job `98094435518` (`Isolated Component Validation Testing`) failed during `docker compose up -d transient-memory-grid` with repeated duplicate-key errors for `version`, `services`, and `networks`.

## Replacement decision

Replace the active file with one canonical Compose document whose services have explicit dependency boundaries. Optional capabilities may be represented as separately selectable services/profiles, but the core API must not depend on an AI provider or another access surface merely to start.
