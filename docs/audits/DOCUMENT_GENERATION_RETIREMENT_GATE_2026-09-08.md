# Document Generation Retirement Gate — 2026-09-08

## Decision

The canonical document path is now the approved path for active civic-action generation. The constitutional objection surface is fully converged on the canonical Case → verified Authority → DocumentDraft → Artifact boundary.

## Consumer inventory

Search of the current repository for `from src.services.document_generator` found only historical `janavani_v2` consumers and the legacy compatibility test. No active canonical application surface currently imports `MultiFormatDocumentEngine` for document generation.

`src/web/constitutional_router.py` no longer imports or invokes `MultiFormatDocumentEngine`; it delegates to `ConstitutionalObjectionCapability`, which uses the shared artifact service.

## Compatibility boundary

`src/services/document_generator.py` remains as a compatibility facade. It delegates rendering to the canonical renderer and performs no dispatch or transmission. It is retained temporarily so historical code/tests do not require a simultaneous destructive migration.

## Historical code

`janavani_v2/src/web/app.py` and `janavani_v2/src/web/worker.py` remain historical trees and are not part of the canonical runtime. Their legacy imports are therefore not treated as active consumers.

## Retirement gate

Do not delete the compatibility facade or remaining legacy renderer solely because active consumers have disappeared. Before deletion, complete:

1. Confirm the compatibility test is migrated or intentionally retained as compatibility-contract coverage.
2. Confirm `src/documents/generate_pdf.py` has no active consumers.
3. Archive any still-useful historical implementation and record its provenance.
4. Run full regression, security, dependency, architecture, and Docker gates.
5. Verify no production runtime imports the retired paths.
6. Delete only after the above evidence is recorded.

## Ecosystem rule

New civic capabilities must consume the shared DocumentDraft → renderer → artifact infrastructure. No new capability may introduce a parallel document engine, transport path, or authority-resolution implementation.

## Branch retirement

The superseded constitutional branches are not candidates for merge. Their changes have been incorporated or superseded by PR #96. Branch deletion is deferred until repository tooling permits deletion and the archive/provenance record is retained.
