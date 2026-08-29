# Repository Cleanup Register — 2026-08-29

## Scope

This register records only cleanup actions supported by direct repository evidence. It is intentionally conservative: empty files are removed only after inspection, and functional/legacy code is not deleted merely because another implementation exists.

## Confirmed empty placeholders removed

The following files were verified as newline-only files and removed from the Case capability convergence branch:

- `src/services/ai_service.py`
- `src/services/classification_service.py`
- `src/services/complaint_service.py`

All three previously contained no executable implementation.

## Important distinction

An empty directory is not itself a defect. Directories such as `src/adapters`, `src/app`, `src/commands`, `src/core`, `src/documents`, `src/domain`, `src/engine`, and `src/capabilities` are architectural namespaces; their ownership and contents must be audited before restructuring.

## Cleanup policy

1. Confirm file content and consumers.
2. Classify as empty placeholder, duplicate, legacy, canonical, or experimental.
3. Remove only confirmed-empty placeholders when no import/reference requires them.
4. For duplicate or legacy implementations: archive/isolate first.
5. Run tests/CI after cleanup.
6. Never equate absence of search results with proof that a file has no runtime consumer.

## Next cleanup targets

- Enumerate all zero-byte/newline-only files.
- Identify duplicate capability implementations.
- Map each runtime entrypoint and deployment workflow to its owner.
- Consolidate shared infrastructure under provider-neutral contracts.
- Keep Telegram/Web/mobile as independent adapters over shared capabilities.
