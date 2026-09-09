# Janavani Authority + Civic Vertical Slice Convergence — 2026-09-09

## Purpose

Record the repository convergence completed on 9 September 2026 for the canonical Authority boundary and the deterministic Case → Evidence → Authority → Document composition path.

## Implemented

- Added `src/capabilities/authority.py` as the shared, provider-neutral Authority lookup boundary.
- Kept authority metadata lookup provider-neutral; public authority data is not treated as a privileged personal-data capability.
- Centralized verified-destination resolution through `AuthorityCapability.require_verified_destination()`.
- Updated `src/capabilities/civic_action_capability.py` to consume `AuthorityCapability` rather than coupling the composition path directly to an Authority repository.
- Preserved backward compatibility by allowing the civic-action capability to construct the shared Authority capability from an existing repository when an explicit capability instance is not supplied.
- Updated `src/platform/composition.py` so the normal application composition creates the shared Authority capability explicitly.
- Added focused tests in `tests/test_authority_capability.py` covering ID lookup, search, verified destination, unverified destination rejection, and missing-authority failure.

## Existing canonical components retained

The repository already contained the canonical Authority domain/repository and the Civic Action composition boundary. The change therefore converges those existing components instead of introducing a duplicate Authority subsystem.

The Civic Action path now has the following application composition:

`owned Case → referenced Evidence validation → Authority capability → verified destination → DocumentDraft → reviewable artifact`

The artifact-generation path remains review/download only. It does not submit or transmit the document.

## Explicitly not claimed

- This does not make the full flagship civic-action vertical slice complete.
- End-to-end production runtime evidence is still required.
- User editing/correction UI is still required.
- Full provenance implementation/verification is still required.
- Submission acknowledgement/tracking remains incomplete.
- Full Python/Rust/Dioxus CI evidence for these newest commits must be verified from GitHub Actions before marking the work COMPLETE.
- Live Render/Vercel runtime verification remains open.

## Commits

- `035cb3a0ce285a1a1e483680034d29302caeb3d2` — initial Authority capability boundary
- `7becd28219f3d3da86d08e82c8facb7a741f9e01` — align Authority capability with provider-neutral public-data boundary
- `4e0b90ff5cb80b0e29154fcd3657fdc487250bec` — route Civic Action authority resolution through shared capability
- `0007d4799b024439da1594b6aaf20bb35511f940` — compose shared Authority capability
- `4515479388f630026e0c84880189fff268c06206` — add Authority capability tests

## Current status

**Authority capability convergence: IMPLEMENTED / VERIFYING**

**Case → Evidence → Authority → Document composition: IMPLEMENTED / VERIFYING**

The next gate is verification, not another architectural generation: run/inspect CI, then complete the remaining vertical-slice requirements in the existing canonical boundaries.
