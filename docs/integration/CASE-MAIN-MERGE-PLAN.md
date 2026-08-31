# Case / Main Integration Plan

Status: preparation only

## Objective
Prepare `main` for a safe integration of the canonical civic case capability without introducing a second Case implementation.

## Findings
- Canonical Case contract: `src/core/civic_case.py`
- Canonical HTTP adapter: `src/web/civic_case_router.py`
- Canonical registration boundary: `src/web/canonical_app.py`
- Case implementation exists on `feat/shared-civic-case-contract` and is not merged into `main`.
- `feat/shared-civic-case-contract` is 4 commits ahead and 32 commits behind `main`; it must not be merged directly without synchronization/review.
- `feat/canonical-case-kernel` is 5 commits ahead and 15 commits behind `main`; it contains separate kernel work and must be evaluated independently.

## Safety Rules
1. Do not force-push `main`.
2. Do not delete Case branches before integration evidence exists.
3. Do not create `case_workflow_router.py` as a compatibility substitute.
4. Do not merge a stale/diverged Case branch directly into `main`.
5. Preserve the distinction between `SUBMITTED` and `ACKNOWLEDGED`.
6. Preserve explicit consent before readiness/submission.
7. Keep channel adapters dependent on the shared Case contract, not the reverse.
8. Run import, unit, API, and canonical startup checks before merge.

## Integration Sequence
1. Keep this preparation branch based on current `main`.
2. Synchronize the canonical Case implementation onto an integration branch from current `main`.
3. Resolve any conflicts in favor of the canonical architecture, not historical duplicate implementations.
4. Run the complete relevant test suite.
5. Verify canonical FastAPI import and `/liveness`/`/version`.
6. Verify civic case lifecycle: create -> consent -> ready -> submit; verify acknowledgement remains distinct.
7. Open a fresh PR from the synchronized integration branch to `main`.
8. Merge only after review and passing checks.
9. Keep original Case branches until post-merge verification is complete.
