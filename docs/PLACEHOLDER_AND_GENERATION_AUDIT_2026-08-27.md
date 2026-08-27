# Janavani — Placeholder / Broken / Generation Audit

**Date:** 27 August 2026  
**Status:** ACTIVE — discovery pass  
**Scope:** empty source placeholders, explicit abstract stubs, likely generated/duplicated runtime generations, and files requiring dependency verification before removal.

## Confirmed empty source placeholders

The following files on `main` were verified to contain only a newline:

- `src/domain/citizen.py`
- `src/domain/department.py`
- `src/domain/document.py`
- `src/domain/evidence.py`
- `src/domain/issue.py`
- `src/domain/location.py`
- `src/domain/office.py`
- `src/domain/remedy.py`
- `src/domain/submission.py`

These are not yet classified as obsolete. They are classified as **empty placeholders** until import/dependency tracing establishes whether they should become canonical domain objects, compatibility modules, or be removed/archive-converted.

## Confirmed abstract contract stub

`src/workflow/base_step.py` defines an abstract `WorkflowStep.execute()` method whose implementation raises `NotImplementedError`. This is valid for an abstract interface by itself and is therefore **not automatically a defect**. It should remain only if concrete workflow steps and tests demonstrate that the contract is actively used.

## Confirmed generation/corruption signals from prior audit

The repository convergence audit records a previously confirmed multi-generation concatenation in `src/web/app.py` and a two-generation `Dockerfile`. Those artifacts were subsequently converged rather than treated as independent runtime generations.

The same audit also identified overlapping generic Python CI workflows and a suspect Django workflow referencing a missing root `manage.py`.

## Strong candidates for further inspection

Search results identify multiple parallel trees and likely historical generations, including:

- `janavani_v2/`
- `janavani_v3/`
- `archive/`
- `docs/archive/legacy/`
- legacy Nostr/Nym/IPFS/blockchain services
- duplicated web routers and webhook adapters
- GPT4All example/install scripts
- multiple generic Python CI workflows

These are **not deletion candidates solely because they are old**. They require import, workflow, deployment, test, and documentation tracing.

## Detection rules for the next pass

Classify a file as:

1. **EMPTY_PLACEHOLDER** — zero/whitespace-only source.
2. **ABSTRACT_CONTRACT** — intentionally incomplete interface/abstract method.
3. **BROKEN** — syntax/import/runtime defect confirmed by verification.
4. **GENERATED_OR_CORRUPTED** — concatenated/duplicated generations or generated output masquerading as source.
5. **LEGACY_ACTIVE_CANDIDATE** — older implementation still referenced by active code.
6. **ARCHIVE_SAFE** — historical and unreferenced after dependency verification.
7. **CANONICAL** — active owner of a capability.

## Decision rule

Do not delete an empty or legacy file merely because a newer implementation exists. First establish whether it is imported, referenced by tests, used by a workflow/deployment target, or named by canonical documentation. Then either implement it as the canonical owner, convert it to an explicit compatibility boundary, or archive/remove it with evidence.

## Immediate next actions

- Trace imports of all nine empty domain placeholders.
- Inspect the active `office_service.py` against the canonical Authority contract.
- Reconcile `GovernmentOrganisation`, `GovernmentOffice`, `GovernmentOfficial`, `ElectedRepresentative`, and `AddressCorrection` from `docs/DATA_CONTRACTS.md` with the new Authority boundary.
- Inspect duplicate v2/v3 routers and adapters for active references.
- Inspect generic CI workflows for redundant or dead entry points.
- Run canonical tests after each convergence unit.
