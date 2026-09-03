# Document Generation Convergence Audit — 2026-09-03

## Decision

The canonical document capability is now the only approved rendering boundary
for new work. Legacy callers may remain behind compatibility facades while
migration evidence is collected.

## Verified legacy consumers

| Consumer | Finding | Decision |
|---|---|---|
| `src/services/document_service.py` | Called legacy PDF generator and had no DOCX implementation | Converged to canonical artifact service |
| `src/services/document_generator.py` | Independent PDF/DOCX renderer | Reduced to compatibility facade over canonical renderers |
| `src/documents/generate_pdf.py` | Own office lookup, composition and PDF rendering | Legacy; retain until remaining consumers are migrated and archived |
| `janavani_v2/src/web/worker.py` | Uses `MultiFormatDocumentEngine` | Protected by compatibility facade; migration later |
| `src/web/constitutional_router.py` | Uses `MultiFormatDocumentEngine` | Protected by compatibility facade; migration later |
| `janavani_v2/src/web/app.py` | Uses `MultiFormatDocumentEngine` | Protected by compatibility facade; migration later |

## Canonical boundary

```text
Surface / legacy caller
        |
        v
Document capability
        |
        +--> DocumentDraft
        |
        +--> PDF / DOCX renderer
        |
        +--> Artifact Blob Store
        |
        +--> Artifact Metadata Repository
        |
        v
User review / print / download
```

## Non-negotiable rule

JanaVani does not send or submit generated documents. Email addresses may be
included as destination metadata when available, but document generation must
never perform transmission. Any action the user takes after download is outside
JanaVani's document-delivery business boundary.

## Archive/delete gate

`src/documents/generate_pdf.py` remains in place because the repository still
contains legacy consumers and historical behavior that must be compared before
removal. Archive first; delete only after consumer inventory, regression tests,
output comparison, and migration evidence are complete.

## Provider independence

Document generation depends on capability contracts, not on Telegram,
Supabase, a specific cloud storage service, or a specific transport. The local
artifact provider is an implementation choice and remains replaceable.
