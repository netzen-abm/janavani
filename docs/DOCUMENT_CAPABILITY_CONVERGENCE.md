# JanaVani Document Capability Convergence

**Status:** IMPLEMENTATION / VERIFYING  
**Date:** 25 August 2026  
**Scope:** Canonical document composition and future rendering/delivery integration

## Purpose

This document records the document-generation convergence introduced during repository cleanup. It is intentionally paired with the implementation so that new architecture is not left undocumented.

## Problem found

The repository contained multiple document-generation generations:

- `src/documents/document_engine.py` expected a `ComplaintBuilder` class with `.build()`.
- `src/documents/complaint_builder.py` exposed a standalone `build_complaint()` function.
- `src/services/document_service.py` separately orchestrated complaint generation and PDF output.
- `src/services/document_generator.py` separately rendered PDF and DOCX streams.
- `src/documents/pdf_generator.py` separately rendered PDF files.
- historical conversation/channel code also contained document-generation behavior.

These implementations created competing ownership and incompatible interfaces.

## Canonical ownership

The converged boundary is:

```text
Interface / channel adapter
        |
        v
Document capability contract
        |
        v
DocumentEngine
        |
        +--> purpose-specific builder
        |
        v
StructuredDocument
        |
        +--> optional legal-analysis enrichment
        |
        +--> renderer (PDF/DOCX/etc.)
        |
        v
channel-specific delivery adapter
```

No channel should own civic document composition or file rendering.

## New contracts

`src/documents/document_contract.py` defines:

- `DocumentRequest` — validated, user-authorized request.
- `StructuredDocument` — channel-neutral composed document.
- `DocumentArtifact` — rendered artifact with format and media type.

Supported document types currently exposed by the contract are complaint, RTI, petition and grievance. Only complaint composition is implemented in this convergence step. The registry remains authoritative for capability completion status.

## Complaint implementation

`src/documents/complaint_builder.py` is now the canonical complaint builder and returns `StructuredDocument`.

It does not render PDF/DOCX and does not perform channel delivery.

## Optional legal enrichment

`src/documents/legal_enrichment.py` is a new capability boundary introduced during this convergence. It defines a small `LegalEnricher` protocol and a deterministic `NoOpLegalEnricher` fallback.

Legal enrichment is explicitly best-effort. If no enricher is supplied, or an enricher fails, document composition continues with `legal_analysis=None`. The structured document provenance records whether enrichment was available.

This prevents legacy legal rules, AI providers, RAG systems or future legal-analysis implementations from becoming hard dependencies of deterministic document composition. Enrichment output is analysis metadata and is not an authoritative legal determination.

## Failure isolation

Document composition must remain available without Telegram, Web, WhatsApp, Messenger, DApp or another client being operational.

Rendering and delivery failures must not corrupt the underlying structured draft.

AI/provider/legal-enrichment failure must not become an unnecessary dependency for deterministic document construction.

## Archive-first migration rule

The previous `document_engine.py` implementation has been copied to:

`docs/archive/legacy/src/documents/document_engine.py`

No deletion is performed as part of this convergence step.

Other duplicate renderers remain candidates until import, runtime and test evidence establishes whether they can be safely archived.

## Required verification

Before promoting this capability beyond `IMPLEMENTATION` / `VERIFYING`, test:

1. complaint composition contract;
2. invalid document type rejection;
3. empty issue rejection;
4. PDF rendering;
5. DOCX rendering;
6. artifact metadata/content type;
7. channel-independent invocation;
8. operation when optional legal/AI enrichment is unavailable;
9. no cross-channel imports from document core;
10. migration compatibility for existing callers.

## Future extension

New document types, renderers, signing mechanisms, verifiable credentials, Web3 anchoring, offline packages or future Web paradigms must be added behind the capability contracts rather than embedded in a channel.

The implementation therefore follows:

```text
stable contract
    -> new implementation / adapter
    -> registration
    -> policy / consent
    -> tests
    -> documentation
```

## Documentation rule

Every new implementation introduced during ecosystem convergence must update the relevant architecture/capability documentation in the same change set. Code without corresponding architectural documentation is not considered a complete convergence change.
