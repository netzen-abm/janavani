# Legacy SOS Migration and Ownership Matrix

## Status

Audit evidence only. No legacy implementation is deleted by this document.

## Audit basis

Audited the canonical main line after the SOS/Safety/Privacy and public-service registry merges.

Legacy implementation:
- src/services/emergency_sos.py
- tests/test_emergency_lockdown.py

Historical references in older documents and versioned trees are not treated as active runtime dependencies without current executable evidence.

## Findings

| Legacy behavior | Current owner | Evidence | Canonical destination | Disposition |
|---|---|---|---|---|
| Delete transient_doc:{session_tracking_id} from Redis | emergency_sos.py | Direct code + test | Existing transient/cache storage boundary, if security action is still required | Separate security/cache capability required before retirement |
| Blacklist interface token for 24h | emergency_sos.py | Direct code + test | Authorization/session security boundary, not SOS | Separate security capability required before retirement |
| Construct Nostr Kind-4-style emergency payload | emergency_sos.py | Direct code | Canonical SOS provider-neutral delivery boundary, only if Nostr is actually required | Do not migrate blindly |
| Claim cache purge completed | emergency_sos.py | Direct code | Truthful storage operation result | Retire with legacy engine |
| Claim interface token revoked | emergency_sos.py | Direct code | Canonical authorization/security result | Retire with legacy engine after replacement |
| Claim Nostr distress signal dispatched | emergency_sos.py | Direct code | Canonical SOS delivery state | Retire; never claim dispatch without provider evidence |
| POST /api/v1/agent/trigger-sos historical ownership | nginx + architecture docs | Repository search | Canonical SOS surface adapter, if route remains active | Requires current runtime route verification |

## Critical architectural conclusion

The old class is not merely an older spelling of canonical SOS. It combines emergency orchestration, transient data/security cleanup, and Nostr notification construction.

The canonical SOS boundary already owns emergency orchestration. The other behaviors require independent ownership decisions.

Retirement sequence:

    Legacy SOS
       |
       +--> emergency orchestration ----> canonical SOS
       |
       +--> cache deletion --------------> security/cache boundary OR obsolete
       |
       +--> token revocation ------------> authorization/session boundary
       |
       +--> Nostr notification ----------> provider-neutral delivery, only if required
       |
       +--> legacy status claims --------> truthful canonical result semantics

## Current executable dependency evidence

Search on the current repository line found:

- tests/test_emergency_lockdown.py directly imports JanavaniEmergencySOSEngine.
- src/services/emergency_sos.py is the current source definition found for that class.
- trigger_crisis_lockdown is directly tested.
- /api/v1/agent/trigger-sos remains referenced by nginx.conf and architecture documentation; its current canonical runtime mounting still requires verification.
- transient_doc: is used by the active cache implementation as well as historical v2/v3 trees.
- security:blacklisted_tokens: appears in the legacy engine/test and historical v3 metrics code.

Deletion of the legacy class is therefore not yet justified.

## Required next verification

1. Verify whether /api/v1/agent/trigger-sos is actually mounted by the canonical runtime.
2. Verify whether the current authorization/session system has a live consumer of security:blacklisted_tokens:.
3. Determine whether emergency-triggered cache deletion is a current product/security requirement or legacy behavior.
4. Decide whether Nostr emergency notification remains a supported Janavani capability. If yes, implement it only behind the canonical delivery boundary.
5. Replace legacy tests with focused tests for canonical owners before archiving the legacy test and implementation.

## Explicit non-actions

This audit does not delete the legacy files, add a Redis security engine, add a Nostr provider, add a police HTTP provider, add autonomous emergency escalation, weaken Architecture Guard, or migrate storage/database providers.

## Archive-first rule

No deletion is authorized by this document. Any future removal must first preserve the file in the repository archive/history and provide evidence that the canonical replacement is active and tested.
