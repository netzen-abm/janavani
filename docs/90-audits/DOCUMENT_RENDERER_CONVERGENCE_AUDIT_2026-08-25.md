# Document Renderer Convergence Audit — 2026-08-25

**Status:** Active convergence audit  
**Branch:** `refactor/document-capability-convergence`  
**Rule:** Evaluate → Audit → Compare → Modify/Merge → Archive → Delete only with evidence

## Scope

This audit records the document-generation convergence work and prevents multiple active renderer generations from silently becoming competing architecture.

## Canonical ownership

The active document path is:

```text
DocumentRequest
    ↓
DocumentEngine
    ↓
StructuredDocument
    ↓
DocumentRenderer
    ↓
RendererRegistry
    ├── PdfRenderer
    └── DocxRenderer
```

`DocumentEngine` owns document composition. It does not own rendering or delivery. Renderers convert a `StructuredDocument` into a `DocumentArtifact`. `RendererRegistry` resolves renderers by declared format.

## Evidence reviewed

### Canonical implementation

- `src/documents/document_engine.py`
- `src/documents/document_contract.py`
- `src/documents/renderer.py`
- `src/documents/renderers.py`
- `src/documents/pdf_renderer.py`
- `src/documents/docx_renderer.py`
- `tests/test_document_generation.py`

### Legacy active candidates

- `src/documents/pdf_generator.py`
- `src/services/document_generator.py`
- `src/documents/generate_pdf.py`

### Archived generations

- `docs/archive/legacy/src/services/document_generator.py`
- `docs/archive/legacy/src/documents/generate_pdf.py`
- other archived document-generation files under `docs/archive/legacy/`

## Findings

### 1. Multiple active rendering implementations existed

`PDFGenerator` directly renders text to PDF. `MultiFormatDocumentEngine` independently renders text to PDF and DOCX. `generate_pdf.py` independently renders complaint data through WeasyPrint/Pandas and also contains a backward-compatibility wrapper.

These implementations duplicate rendering ownership and bypass the channel-neutral `StructuredDocument → DocumentArtifact` boundary.

### 2. The canonical renderer boundary is now explicit

PDF and DOCX implementations are separated into replaceable renderer classes and resolved through `RendererRegistry`. Tests verify the returned artifact format, media type, binary type and basic file signature.

### 3. Capability contract and implementation status must not be conflated

The document contract declares multiple document types, while the current `DocumentEngine` implementation only handles `complaint`. Therefore RTI, petition and grievance generation must not be described as implemented until corresponding composition implementations and tests exist.

### 4. Legacy files are not yet candidates for destructive deletion

No deletion is authorized solely because a canonical renderer exists. Before deletion, each active legacy candidate requires reference/import tracing, consumer migration evidence, test coverage and confirmation that compatibility requirements have been preserved.

## Disposition

| File/family | Current disposition | Required next action |
|---|---|---|
| `src/documents/document_engine.py` | CANONICAL | Keep; extend only through contracts |
| `src/documents/document_contract.py` | CANONICAL | Keep; reconcile status with implementation |
| `src/documents/renderer.py` | CANONICAL CONTRACT | Keep |
| `src/documents/renderers.py` | CANONICAL REGISTRY | Keep |
| `src/documents/pdf_renderer.py` | CANONICAL IMPLEMENTATION | Keep; test |
| `src/documents/docx_renderer.py` | CANONICAL IMPLEMENTATION | Keep; test |
| `src/documents/pdf_generator.py` | LEGACY / ARCHIVE CANDIDATE | Trace references; archive before any deletion |
| `src/services/document_generator.py` | LEGACY / ARCHIVE CANDIDATE | Trace references; archive before any deletion |
| `src/documents/generate_pdf.py` | LEGACY / ARCHIVE CANDIDATE | Trace references; migrate compatibility consumers; archive before any deletion |
| archived renderer generations | HISTORICAL | Preserve; do not treat as active authority |

## Safety and privacy implications

Document rendering must remain channel-neutral and must not acquire transport, database, messaging or AI-provider dependencies. User-selected optional use of a renderer or channel does not remove the capability from the ecosystem.

Sensitive document content must remain within the existing privacy, authorization and data-boundary controls. Renderer convergence must not bypass those controls.

## Next implementation steps

1. Trace all imports and runtime references to legacy document generators.
2. Migrate any remaining consumers to `DocumentEngine` + `RendererRegistry`.
3. Add compatibility tests where legacy interfaces were externally observable.
4. Reconcile capability registry status for complaint/RTI/petition/grievance.
5. Archive superseded active files only after reference and test evidence.
6. Delete only in a later, separately evidenced cleanup decision.
7. Update the shared infrastructure and document architecture records in the same change set whenever implementation changes.

## Decision

The repository should have **one active document composition boundary and one active renderer boundary**. New formats must be added as independent renderer implementations, not as new generators or client-specific rendering stacks.
