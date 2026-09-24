# Janavani — Document Access-Path Security Audit

**Date:** 24 September 2026  
**Scope:** document drafting, review, artifact generation, approval and submission paths on `main`.

## Executive conclusion

The canonical civic-action path is structurally sound: access surfaces authenticate, Case ownership is enforced by shared capabilities, document review is owner-scoped, and direct HTTP Case submission is explicitly disabled in favor of `SubmissionCapability`.

No new document-generation framework should be introduced.

Two convergence gaps remain:

1. The constitutional-objection capability has a legitimate domain-specific composition boundary, but it persists/render artifacts directly instead of using the canonical `DocumentReviewCapability` persistence boundary.
2. The Telegram generation path correctly uses canonical Case → Evidence → Authority → Document composition, but it is still a legacy-compatible generation surface rather than the newer `LetterDraftingCapability` when a letter is being drafted.

These should be converged selectively; neither warrants arbitrary class/file splitting.

## Verified paths

### Web civic document

`src/web/civic_case_document_router.py`

- authenticated identity required;
- draft preparation delegates to canonical civic-action composition;
- edits delegate to `DocumentReviewCapability`;
- artifact generation uses the canonical vertical slice;
- response explicitly reports `submission: not_submitted`.

### Case submission

`src/web/civic_case_lifecycle_router.py`

The direct `/{case_id}/submit` route is fail-closed and returns HTTP 409. Submission must go through `SubmissionCapability`, which owns authorization, consent, approval, idempotency, delivery and reconciliation.

### Canonical submission orchestration

`src/capabilities/civic_action_vertical_slice.py`

Destination selection is verified through `ExternalChannelCapability` before the request reaches `SubmissionCapability`. An arbitrary caller-supplied destination cannot replace the verified channel destination.

## Convergence gaps

### Constitutional objection

`src/capabilities/constitutional_objection.py` is a legitimate domain-specific drafting boundary because constitutional-objection composition depends on a legislative profile and constitutional evaluation.

However, its artifact path currently performs its own document persistence/case mutation. The independent boundary is the **content composition**, not a second document persistence authority.

Target:

```text
ConstitutionalObjectionCapability
        ↓
DocumentDraft
        ↓
canonical DocumentReviewCapability
        ↓
shared artifact service
```

Do not split constitutional composition into multiple small modules unless a separate provider, trust, persistence or reuse boundary emerges.

### Telegram

`src/conversation/steps/generate.py` uses `CivicActionCapability.generate_reviewable_artifact()`, which is architecturally safer than the historical document generators, but letter-specific drafting should eventually enter through `LetterDraftingCapability`.

The Telegram surface must remain an adapter; it must not gain its own letter composition rules.

## AI boundary

`src/services/legal_agent.py` is currently an optional AI adapter, but it directly knows the OpenRouter HTTP endpoint. That is a provider-dependency boundary.

The next AI convergence should therefore be:

```text
Drafting capability
      ↓
purpose-bound AI request
      ↓
AI provider contract
      ↓
OpenRouter / Ollama / future provider
```

The provider must receive only the selected task payload. AI failure must degrade to deterministic/manual drafting.

Do not introduce RAG or fine-tuning into the core document workflow until source/version/citation and provider contracts are established.

## Repository hygiene

The repository currently contains exactly nine active branches. No additional branch should be created for this work unless one of the nine sanctioned branches is retired and replaced under the archive-first procedure.

Historical branches should be selectively extracted, archived and then retired; wholesale merges of substantially stale architectures are prohibited.

## Acceptance criteria for the next convergence

- one canonical document review persistence authority;
- no surface-specific document composition;
- no direct submission from document rendering;
- verified Case ownership before document access;
- evidence references must resolve to the Case;
- legal framework requires jurisdiction/context;
- AI output remains distinguishable from evidence and verified authority;
- provider failure leaves a deterministic/manual path;
- artifact generation remains separate from external delivery;
- nine active branches remain exactly nine.
