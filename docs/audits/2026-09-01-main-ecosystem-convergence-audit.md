# Janavani — Main Ecosystem Convergence Audit

Date: 2026-09-01
Repository: `netzen-abm/janavani`

## Executive decision

Current `main` is the authoritative baseline. Historical branches must not be merged wholesale because many are based on substantially older `main` snapshots. Valuable work should be extracted capability-by-capability and reconciled against current `main`.

## Verified repository state

- Remote `main` is substantially ahead of the local Codespace checkout shown during the audit.
- The Codespace working tree contains 15 modified files and untracked audit material. Those changes are not safe to push wholesale because they are based on an older commit.
- The exported Codespace branch is 1 commit ahead of its old base but 428 commits behind current `main`.
- The exported Codespace commit contains both source changes and test/demo database mutations. Database fixture mutations must not be promoted to production state without deliberate review.
- Current `main` has six active GitHub Actions workflows. The stale local listing showing 20+ workflows is therefore not the current remote state.

## Active workflow policy

The current remote workflow surface is:

1. `ci.yml` — canonical build/test validation.
2. `dependency-review.yml` — dependency security review.
3. `docker-publish.yml` — container publishing; retain only while container publishing remains an active deployment requirement.
4. `label.yml` — repository pull-request triage automation.
5. `security-ci.yml` — security-specific validation.
6. `verify-decentralized-stack.yml` — validation for the optional decentralized ecosystem layer.

GitHub starter/deployment workflows such as Django, Jekyll, OpenShift, Octopus Deploy, generic Python package publishing, greetings, stale automation, and duplicate Docker validation have already been removed from current `main` through the cleanup sequence. Do not recreate them.

## Code findings

### 1. Conversation session duplication — fixed in this branch

`src/conversation/session.py` contained two definitions of `get_session()` and two independent dictionaries (`sessions` and `user_sessions`). The second definition shadowed the first. This is a concrete correctness and maintainability defect. The branch consolidates the session store to one implementation.

### 2. Runtime entrypoint ambiguity — fixed in this branch

`src/main.py` was a test/demo harness that directly called legacy services and PDF generation rather than acting as the canonical application entrypoint. `src/bot_telegram.py` already contains the actual Telegram application bootstrap. This branch makes `src/main.py` delegate to that canonical transport entrypoint.

### 3. Document capability duplication — requires next convergence pass

Document generation currently spans `document_engine.py`, `document_service.py`, `complaint_builder.py`, `generate_pdf.py`, and `pdf_generator.py`. These must converge behind one document capability contract. Compatibility facades may remain temporarily, but there must be one authoritative generation path per format.

### 4. Legacy web boundary — requires next convergence pass

The repository still contains legacy Flask surfaces alongside the canonical web boundary. These must be mapped to consumers before removal. Do not delete an adapter merely because it is old; first prove whether it is active, referenced, or required by an independently deployable ecosystem surface.

### 5. Office capability duplication — requires next convergence pass

Office functionality is distributed across office services, search services, repositories, and domain/model layers. The long-term target is a shared authority/office capability consumed by all transports rather than transport-specific implementations.

## Safety rules for branch deletion

A branch is safe to delete only when all are true:

- its unique valuable commits are already represented in current `main` or intentionally archived;
- no open PR depends on it;
- it is not the source of an active deployment or integration;
- it contains no unique security or capability contract still required;
- its diff against current `main` is empty or entirely superseded/obsolete;
- the relevant work has verification evidence.

The branch itself is not proof that work is obsolete. Commit ancestry and unique file changes must be checked first.

## Codespace changes

The Codespace changes remain preserved on `origin/codespace-organic-train-r4vvpwrgwwvr3w5rj`. They must be treated as an evidence source, not as a merge target. In particular, its database mutations include duplicate and synthetic complaint records and should not be merged into production data automatically.

## Next convergence targets

1. Canonical case capability.
2. Shared authority/office and evidence capability.
3. Canonical document capability with PDF/DOCX output and print/download-only delivery semantics.
4. Shared storage boundary.
5. Transport adapters (Telegram, Web, WhatsApp, Messenger) consuming the same capabilities without coupling their failure domains.
6. AI policy/capability layer as optional, explicitly user-controlled infrastructure.

## Verification limitation

Local evidence supplied during the audit shows `compileall`, `pytest -q`, and `pip check` succeeding, while Ruff was unavailable and `tools/audit_requirements.py` did not exist. GitHub CI must therefore become the authoritative repeatable verification mechanism rather than relying on ad-hoc Codespace commands.
