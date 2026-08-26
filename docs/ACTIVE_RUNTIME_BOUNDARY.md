# Janavani Active Runtime Boundary

**Status:** ACTIVE ENGINEERING POLICY  
**Date:** 26 August 2026

## Purpose

Janavani contains current runtime code as well as archived, historical, experimental and superseded generations. Active CI must validate the current runtime without requiring obsolete historical material to satisfy present-day lint or application checks.

## Active boundary

The default active Python runtime is:

- `src/`
- `tests/` for active automated tests

Repository-level configuration, deployment manifests and explicitly selected integration assets may also be validated by their dedicated workflows.

## Archive boundary

Historical material under `archive/`, legacy generations and explicitly superseded artifacts are preserved for traceability. They are not part of the active runtime unless a current dependency or dedicated archival verification workflow explicitly requires them.

Archival status does **not** mean the material is trusted or production-ready. It means the material is retained history and must not silently become an active dependency.

## CI rule

Active-runtime lint and static checks should target the active boundary. Archive/legacy validation must be explicit and separate.

This prevents historical defects from masking current defects while preserving the repository's history.

## Change-control rule

No file is archived, deleted or reclassified solely to make CI pass. Before changing a boundary, verify:

1. active imports/dependencies;
2. runtime entry points;
3. tests and CI references;
4. deployment references;
5. replacement availability where applicable;
6. historical value and migration context.

## Relationship to architecture

This policy implements the repository's archive-over-delete principle and the master checklist completion rule. It does not change product scope. Janavani remains a full ecosystem; this boundary only distinguishes **current executable implementation** from **preserved historical material**.
