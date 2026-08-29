# Janavani Repository Audit Tool

## Purpose

`python scripts/janavani_repo_audit.py` is a read-only repository hygiene tool for Janavani contributors and maintainers.

Its purpose is to detect likely cleanup and security-review candidates early, especially while the repository is converging multiple historical generations of code.

## What it checks

The current version reports:

- **EMPTY** — zero-byte or whitespace-only text files.
- **PLACEHOLDER** — common placeholder markers such as `TODO`, `FIXME`, `NotImplementedError`, and implementation placeholders.
- **GENERATED** — common generated-code markers such as `DO NOT EDIT` or `auto-generated`.
- **MUTABLE_ACTION** — GitHub Actions referenced by release/tag/branch rather than a 40-character commit SHA.
- **BROAD_PERMISSIONS** — selected workflow permission patterns that deserve review.

## Usage

From the repository root:

```powershell
python scripts/janavani_repo_audit.py .
```

You may also provide another repository path:

```powershell
python scripts/janavani_repo_audit.py C:\path\to\janavani
```

The tool makes **no changes** to the repository.

## How to interpret findings

A finding is a review candidate, not an automatic defect.

### EMPTY

Confirm whether the file is intentionally empty. If it is an accidental placeholder, remove it through normal Git review.

### PLACEHOLDER

Determine whether the marker represents unfinished production behavior, a legitimate future task, test fixture text, or documentation.

### GENERATED

Do not edit generated files directly unless the generation process is also updated. First identify the generator and its canonical source.

### MUTABLE_ACTION

For production CI, prefer immutable commit-SHA pins:

```yaml
uses: owner/action@<40-character-commit-sha> # vX.Y.Z
```

This improves reproducibility and reduces the risk of a moving tag being changed upstream.

### BROAD_PERMISSIONS

Review whether the workflow actually needs write access. Follow least privilege and keep untrusted pull-request code away from privileged execution contexts.

## Cleanup policy

Janavani uses this sequence:

```text
AUDIT
  -> EVIDENCE
  -> CLASSIFY
  -> FIX / CONVERGE / ARCHIVE
  -> TEST
  -> VERIFY
```

Do not automatically delete findings.

For historical code:

```text
empty placeholder      -> delete when confirmed
useful duplicate       -> converge into canonical owner
historical/uncertain   -> isolate or archive
confirmed obsolete     -> archive, verify, then delete
canonical code         -> strengthen and test
```

## Canonical ownership

The audit tool supports the broader repository rule that a shared capability should have one canonical owner and stable contracts. Access surfaces such as Web, Telegram, WhatsApp, Messenger, API, and future decentralized clients should consume shared capabilities rather than independently implementing the same business rules.

See `docs/audits/CANONICAL_OWNERSHIP_MAP_2026-08-29.md` for the current ownership map.

## CI integration

The tool is currently intended for local and review use. It should be added as a CI gate only after its findings have been validated against the repository and false-positive handling is understood.

A future CI mode may expose explicit checks such as:

```text
janavani-audit --all
janavani-audit --security
janavani-audit --architecture
```

Those modes should remain deterministic and should fail only on clearly defined policy violations.

## Extending the tool

Keep it dependency-free where practical. New checks should:

1. be deterministic;
2. avoid network access;
3. avoid modifying files;
4. explain why a finding matters;
5. distinguish review candidates from confirmed defects;
6. include tests before becoming a CI gate.

## For contributors

Run the audit before opening a large cleanup PR. If it reports a generated file, duplicate implementation, or security-sensitive workflow, investigate the canonical source before editing the symptom.
