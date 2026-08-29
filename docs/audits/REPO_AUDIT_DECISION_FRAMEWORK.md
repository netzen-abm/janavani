# Janavani Repository Audit — Decision Framework

## Purpose

Provide a repeatable method for classifying repository findings before cleanup. This document complements the canonical ownership map and cleanup register.

## Classification

Every significant finding should be assigned one of:

| Class | Meaning | Default action |
|---|---|---|
| KEEP | Canonical, active, or required | Maintain and test |
| CONVERGE | Useful but duplicated or misplaced | Move/adapt toward canonical owner |
| ARCHIVE | Historical or uncertain; not required for current runtime | Isolate with provenance |
| DELETE | Confirmed obsolete and unused | Remove after dependency evidence |
| INVESTIGATE | Evidence is insufficient | Do not modify yet |
| EXPERIMENTAL | Deliberately non-canonical experiment | Keep isolated and clearly labelled |

## Evidence standard

Before changing a file, check as applicable:

1. imports/references;
2. runtime entrypoints;
3. tests and fixtures;
4. deployment workflows;
5. Docker/build configuration;
6. package/dependency manifests;
7. documentation and operational scripts;
8. generated-file provenance;
9. configuration references;
10. Git history when current evidence is ambiguous.

Search absence is never sufficient by itself to prove that a file is unused.

## Legacy-generation signals

A file should be reported as a **legacy-generation candidate**, not automatically classified as obsolete, when multiple evidence signals indicate that another implementation may supersede the same capability.

Useful signals include:

- parallel modules with substantially overlapping names or responsibilities;
- older and newer import paths exposing similar domain operations;
- multiple implementations of the same interface or contract;
- duplicated storage/provider/transport implementations;
- historical configuration pointing to an older module;
- tests covering an older implementation while newer code exists;
- deployment or entrypoint configuration selecting one generation over another;
- documentation identifying a newer canonical implementation;
- explicit migration/deprecation markers;
- Git history showing a replacement or migration sequence.

### Evidence scoring guidance

A future auditor may assign confidence using a small number of independent signals:

```text
LOW
  one weak naming/reference signal

MEDIUM
  multiple independent structural signals

HIGH
  capability overlap + canonical owner + runtime/migration evidence
```

No score should directly trigger deletion. A high-confidence legacy signal should trigger a human review against the canonical ownership map and runtime evidence.

### Example

```text
legacy implementation
       ↓
replacement implementation
       ↓
canonical contract
       ↓
active runtime consumers
```

Only when the evidence shows that the legacy implementation has no required consumer should it move from `INVESTIGATE`/`ARCHIVE` to `DELETE`.

## Duplicate detection

Exact duplicate content is a strong signal but not proof that one copy can be deleted. Semantically duplicated implementations may have different consumers or contracts and require convergence analysis.

## Orphan detection

An orphan signal means only that no obvious textual reference was found. Dynamic imports, CLI entrypoints, deployment systems, scheduled jobs, generated configuration, and external callers can bypass simple search.

## Cleanup sequence

```text
AUDIT
  ↓
COLLECT EVIDENCE
  ↓
CLASSIFY
  ↓
CONVERGE / ARCHIVE / DELETE
  ↓
TEST
  ↓
VERIFY RUNTIME
  ↓
UPDATE DOCUMENTATION
```

## Canonical ownership rule

Shared business capabilities should have one canonical contract and implementation. Access surfaces such as Web, Telegram, WhatsApp, Messenger, API, and future decentralized clients consume those capabilities through adapters rather than creating parallel business logic.

The current ownership baseline is recorded in `docs/audits/CANONICAL_OWNERSHIP_MAP_2026-08-29.md`.

## Audit output requirements

Future Janavani-owned audit tools should preferably produce:

- human-readable findings;
- stable finding categories;
- file/path references;
- severity or confidence where meaningful;
- machine-readable output when practical;
- no automatic destructive action by default.

## Change control

Any cleanup that removes a potentially functional implementation should record the evidence and classification in the repository cleanup register or an equivalent audit record.
