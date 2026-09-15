# Janavani — `main` Branch Ruleset

**Status:** RECOMMENDED CONFIGURATION  
**Applies to:** `main`  
**Purpose:** protect the canonical integration branch without blocking the current solo/development workflow unnecessarily.

## Recommended GitHub ruleset

### Target

- Branch: `main`
- Ruleset enforcement: **Active** once verified against the repository's actual GitHub administration settings.

### Pull-request protection

- Require a pull request before merging: **ON**
- Required approvals: **0 for the current solo-maintainer phase**
- Dismiss stale approvals: **ON** when approvals are later introduced
- Require review from Code Owners: **OFF for now** unless a CODEOWNERS policy is established
- Require conversation resolution: **ON**
- Require branches to be up to date before merging: **ON** when practical

The zero-approval setting is deliberate: the project currently has a single primary maintainer/developer workflow. Raising this to one approval later is recommended when independent maintainers are available.

### Required status checks

Require the repository's canonical deterministic gates before merging:

- `CI`
- `Architecture Guard`
- `Security CI`
- `Dependency review`
- `Docker`

The exact check names should be selected from the checks GitHub exposes for `main`; do not invent or hard-code a check that is not actually reported by the repository.

### History protection

- Block force pushes: **ON**
- Block branch deletion: **ON**
- Require linear history: **OFF** for now because Janavani has intentionally used normal merge commits for bounded PR integration.

### Commit/signature policy

- Require signed commits: **OFF for now**

This should be enabled only after the maintainer signing workflow is established and tested. Security should not be weakened by creating an untested operational requirement.

### Bypass policy

Avoid routine bypasses. If GitHub requires a bypass actor for emergency recovery, restrict it to the minimum administrative actor and document every bypass in the repository change record.

### AI/code-review checks

Do **not** make the GitHub Advanced Security AI review a required merge check at this stage.

PR #165 demonstrated why: the AI workflow can fail because of an unsupported model/service condition even when the repository's deterministic CI, architecture, dependency, Docker, and security gates are green. Such an external availability failure must not be confused with a code-security finding.

Deterministic repository gates remain authoritative for merge readiness.

## Merge policy

The project should continue to use this sequence:

```text
feature/chore branch
        ↓
Pull Request
        ↓
Deterministic gates
        ↓
Final diff/security review
        ↓
Normal merge into main
```

Do not permit direct routine pushes to `main`.

## Relationship to Janavani's architecture rule

This ruleset protects the integration boundary; it does not replace the repository's Architecture Guard. Architecture decisions remain expressed in code contracts and architecture documentation, while GitHub rules enforce the minimum integration controls.

## Future tightening

When the project moves from solo development to multi-maintainer or production operation, reassess:

1. one or more independent approvals;
2. CODEOWNERS for architecture/security-sensitive paths;
3. signed commits;
4. stricter bypass controls;
5. required code-scanning/security checks after their availability is proven stable;
6. release/tag protection.

**Principle:** protect `main` strongly, but do not turn external or immature tooling into an accidental single point of failure for the development lifecycle.
