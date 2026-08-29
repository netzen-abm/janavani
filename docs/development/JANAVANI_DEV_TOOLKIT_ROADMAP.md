# Janavani-Owned Developer Toolkit Roadmap

## Purpose

Janavani should progressively own the project-specific engineering intelligence needed to build, maintain, audit, and operate the ecosystem.

The goal is **not** to eliminate third-party software. Mature external tools should be used when they provide a strong, well-maintained capability. Janavani-owned tools should be created when the requirement is project-specific, strategically important, repeatedly needed, or poorly served by generic tooling.

## Guiding principle

```text
Need identified
    -> Check GitHub / OS / standard library
    -> Check mature OSS alternatives
    -> Evaluate cost, trust, maintenance, portability, and lock-in
    -> Use external capability when it is clearly better
    -> Build Janavani-owned capability when the requirement is strategic or project-specific
```

## Design principles

Every Janavani-owned tool should, where practical:

1. be small and composable;
2. prefer Python standard library or existing project dependencies;
3. avoid unnecessary network access;
4. be deterministic;
5. have a documented CLI or API contract;
6. be read-only by default for audit tools;
7. include tests before becoming a CI gate;
8. have clear ownership and lifecycle status;
9. produce machine-readable output when useful;
10. fail safely and explain its findings;
11. avoid duplicating mature infrastructure without a concrete reason;
12. remain reusable across Web, API, bots, AI, data, and future interfaces.

## Tool lifecycle

```text
EXPERIMENTAL
    -> INTERNAL
    -> STABLE
    -> CANONICAL
```

A tool should not become a CI gate merely because it exists. Its findings and failure modes must first be validated against the repository.

## Roadmap

### Phase 1 — Repository intelligence

**Status: ACTIVE**

- `janavani_repo_audit.py`
  - empty-file detection
  - placeholder detection
  - generated-code markers
  - mutable GitHub Action references
  - broad workflow permissions
- Expand it with:
  - duplicate implementation detection
  - orphan-file detection
  - legacy-generation detection
  - suspicious configuration detection
  - report/JSON output

### Phase 2 — Architecture intelligence

**Planned**

`janavani_arch_audit`

Potential checks:

- canonical ownership violations;
- forbidden dependency direction;
- capability boundary violations;
- duplicated business logic;
- adapter/interface consistency;
- deprecated module usage;
- public API contract drift.

### Phase 3 — Workflow and CI intelligence

**Planned**

`janavani_workflow_audit`

Potential checks:

- action pinning;
- permissions analysis;
- unsafe workflow triggers;
- secret exposure patterns;
- duplicate workflows;
- obsolete workflow references;
- required CI coverage.

Third-party tools such as Actionlint and Zizmor remain useful here because they provide mature generic analysis; Janavani tooling should add project-specific policy rather than duplicate them.

### Phase 4 — Dependency intelligence

**Planned**

`janavani_dependency_audit`

Potential checks:

- direct versus transitive dependencies;
- unused dependencies;
- duplicate libraries;
- dependency ownership;
- runtime/build dependency separation;
- policy exceptions;
- dependency age and maintenance signals.

External vulnerability databases may remain the authoritative source for vulnerability intelligence.

### Phase 5 — Data and privacy intelligence

**Planned**

`janavani_data_audit`

Potential checks:

- PII/identity-bearing data locations;
- local-only versus server-stored data;
- retention classification;
- logging of sensitive fields;
- provenance requirements;
- data minimization;
- public/private data boundary violations.

This is particularly important as Janavani expands citizen, complaint, identity, and governance capabilities.

### Phase 6 — Capability completeness

**Planned**

`janavani_capability_audit`

Potential checks:

- capability specification exists;
- canonical implementation exists;
- interface/contract exists;
- tests exist;
- adapters exist where required;
- observability exists;
- documentation exists;
- deprecated parallel implementation exists.

The objective is to prevent a capability from being represented by documentation or stubs without a working implementation.

### Phase 7 — Migration and convergence intelligence

**Planned**

`janavani_migration_audit`

Potential checks:

- old-to-canonical module mapping;
- stale imports;
- deprecated APIs;
- duplicated storage paths;
- legacy configuration;
- migration completeness;
- orphaned historical code.

This will become especially valuable during ecosystem convergence.

### Phase 8 — Release intelligence

**Planned**

`janavani_release_audit`

Potential checks:

- artifact existence;
- version consistency;
- test status;
- SBOM presence;
- provenance presence;
- signature presence;
- container metadata;
- release documentation;
- policy compliance.

This tool should complement, not replace, mature signing/provenance technologies.

## Proposed unified CLI

As the toolkit grows, expose a single developer-facing command:

```text
janavani-audit --all
janavani-audit --repo
janavani-audit --architecture
janavani-audit --workflow
janavani-audit --dependencies
janavani-audit --data
janavani-audit --capabilities
janavani-audit --migration
janavani-audit --release
```

The initial implementation may remain as individual scripts. Consolidation should happen only when there is enough stable functionality to justify a package/CLI.

## Third-party tool policy

Janavani should use third-party tools when they are:

- mature;
- actively maintained;
- auditable;
- appropriately licensed;
- materially better than a small internal implementation;
- not introducing unnecessary lock-in or sensitive-data exposure.

Examples of capabilities that are reasonable to retain externally include generic CodeQL analysis, dependency vulnerability databases, container signing, provenance standards, and general GitHub Actions security analysis.

Janavani-owned tooling should focus on the **Janavani-specific policy and architecture knowledge** around those systems.

## What we should not build

Do not build internal replacements merely for the sake of independence when a mature standard already solves the problem well. Examples include cryptographic primitives, general-purpose compilers, mature vulnerability databases, container runtimes, and generic version-control functionality.

## Long-term objective

The Janavani Developer Toolkit should become a lightweight internal infrastructure layer that helps developers answer:

```text
What is real?
What is canonical?
What is duplicated?
What is obsolete?
What is unsafe?
What is incomplete?
What changed?
What can be released safely?
```

The toolkit should make the repository progressively easier to understand and harder to accidentally degrade as the Janavani ecosystem grows.
