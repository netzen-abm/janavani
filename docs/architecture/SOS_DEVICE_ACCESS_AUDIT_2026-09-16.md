# SOS & Device-Access Boundary Audit — 2026-09-16

## Scope

Whole-repository review of SOS, emergency dispatch, camera, microphone/audio, location/GPS, contacts, biometric/face processing, local device wiping, external emergency dispatch, and related permission/data-access paths on the `main` baseline `9330757f096eda8c29f55e1db2dc27e7e7904a65`.

The purpose is boundary classification before implementation. No runtime behavior is changed by this audit.

## Governing boundaries

The canonical direction is capability-first, surface-independent, privacy/safety by design, purpose-bound device access, explicit user choice, truthful delivery state, and reuse of the existing authorization/consent/evidence primitives. A new safety/privacy policy engine must not be introduced.

## Findings

| Path | Finding | Classification | Disposition |
|---|---|---|---|
| `src/services/emergency_sos.py` | Constructs a Redis client at service construction, directly deletes cache keys, directly revokes interface tokens, and constructs a Nostr emergency event. It reports successful dispatch without an actual Nostr transport operation. | Transitional / violation | Do not extend. Replace behind canonical SOS, storage/provider, authorization, evidence, and external-action contracts. Archive only after replacement and evidence. |
| `janavani_v2/src/sos.rs` | Legacy SOS engine directly invokes Reticulum mesh, clears browser storage globally, and reports a completed wipe/mesh action. | Legacy / violation | Preserve as historical evidence for now. Do not wire into current runtime. Archive/move only through the archive-first process once repository dependency evidence permits. |
| `src/web_dioxus/src/sos_interface.rs` | Directly chooses online/offline transport, contains a hard-coded backend URL and interface token, directly invokes Reticulum, globally clears local storage, and reports successful routing based on HTTP success. | Transitional / violation | Do not extend. Replace with surface adapter consuming shared SOS + privacy + authorization + transport contracts. Hard-coded credential/path must not become canonical. |
| `janavani_v2/src/web/app.py` | Legacy-generation web path accepts evidence video and location fields directly. | Legacy / review | Keep isolated from canonical runtime until generation status and dependency graph are verified. No new feature work here. |
| `janavani_v2/src/main.rs` | Contains a baseline GPS coordinate in application state and actively invokes the v2 `EmergencySOSEngine`. | Legacy / violation | Treat as legacy generation. Do not wire into current runtime. Verify dependency graph before archive. |
| `janavani_v2/src/web/de-linked_ingestion.py` | Legacy image ingestion strips EXIF/GPS metadata locally. | Legacy / potentially reusable | Useful security idea, but must not become a second privacy engine. Re-express as an implementation detail of canonical evidence/privacy contracts if still needed. |
| `janavani_v3/src/web/de_linked_ingestion.py` | Another generation of the same local metadata-stripping concept. | Legacy / duplicate | Consolidate conceptually; archive only after dependency/evidence verification. |
| `janavani_v3/src/auto_transport.rs` | Legacy v3 transport router directly selects Reticulum/Nym/Internet paths and imports concrete transport drivers. It is reachable from `janavani_v3/src/main.rs`, but remains outside the canonical current Python/WebApp/Telegram runtime. | Legacy generation / violation | Do not extend. Preserve as historical architecture material; replace with provider-neutral transport contract if the capability is revived. |
| `src/web_dioxus/src/main.rs` | Current repository Web Dioxus surface imports and invokes `JanavaniWasmSOSTrigger::dispatch_panic_beacon`. | Active transitional surface / violation | This is the only confirmed active surface reachability found for the legacy SOS trigger in the current Web Dioxus tree. Migrate the surface to the canonical SOS capability before treating the legacy trigger as unreachable. |
| `docs/CAPABILITY_REGISTRY.md` | Canonical capability registry already defines SOS variants and evidence capture, privacy, integrity, offline honesty, human review, and failure-isolation rules. | Canonical | Reuse; no duplicate capability identifiers. |
| `docs/DATA_CONTRACTS.md` | Defines emergency alert opt-in/opt-out and location sharing modes including ask-each-time and preconfigured-for-SOS. | Canonical policy reference | Reconcile implementation against this contract; do not invent another location-sharing policy. |
| `docs/architecture/JANAVANI_SAFETY_AUDIO_EVIDENCE_CONTRACT.md` | Defines audio as first-class evidence with local-first capture, explicit microphone permission, separate upload consent, provenance, truthful delivery states, and separation from face/CV. | Canonical | Use as the audio implementation contract. |
| `docs/architecture/PRIVACY_PURPOSE_BOUND_PERMISSION_CONTRACT.md` | Defines Ask → Explain purpose → Grant → Use → Purpose Complete → Release → Ask Again and separates device access, data sharing, AI, and biometric permissions. | Canonical | Use as the device-access lifecycle contract. |
| `docs/architecture/SAFETY_PRIVACY_DECISION_BOUNDARY.md` | Defines ALLOW/MINIMIZE/BLOCK/REVIEW and delegates capability authorization to the existing authorization kernel. | Canonical pending PR #178 | Do not create another safety/privacy decision engine. |
| `src/access/authorization.py` | Existing canonical authorization kernel evaluates principal/capability/action/resource/risk and can require approval for high-risk actions. | Canonical | Reuse for SOS and consequential actions. |
| `src/capabilities/consent.py` | Existing explicit consent capability provides a canonical consent boundary. | Canonical | Reuse; do not duplicate consent logic. |
| `src/core/evidence.py` / `src/capabilities/evidence.py` | Existing evidence model/capability supports hash, provenance, repository, attachment, and execution-context controls. | Canonical | SOS media/audio evidence should use this path rather than creating a second evidence store. |

## Active reachability trace

The repository search was repeated against the audited `main` baseline using the concrete SOS symbols and module names, rather than relying only on older architecture documents.

### Confirmed active reachability

- `src/web_dioxus/src/main.rs` imports `JanavaniWasmSOSTrigger` and calls `dispatch_panic_beacon(...)`. This makes `src/web_dioxus/src/sos_interface.rs` an actively reachable legacy/transitional SOS path within the Web Dioxus surface. citeturn76file1turn79file0
- `janavani_v3/src/main.rs` declares and imports `auto_transport`, and `janavani_v3/src/auto_transport.rs` directly imports concrete Reticulum/Nym transport drivers. This is reachable inside the legacy v3 generation, not evidence that the current canonical runtime depends on it. citeturn80file0turn77file1
- `janavani_v2/src/main.rs` actively invokes `EmergencySOSEngine::trigger_immediate_security_wipe(...)`, making the v2 SOS path reachable within the v2 application generation. citeturn82file1

### No confirmed current-surface import found

- `src/services/emergency_sos.py` is referenced by its dedicated legacy test and by historical/runtime inventory documents, but the concrete symbol search did not identify a current canonical surface importing `JanavaniEmergencySOSEngine`. The old API ownership map still documents `/api/v1/agent/trigger-sos` as owned by that service, so route registration must be separately verified before archival. citeturn73file1turn73file2turn74file5
- The v2/v3 implementations are therefore not safe to delete merely because they are legacy; they have generation-local reachability and require explicit dependency/reference evidence before archival.

### Consequence

The dependency gate is now materially narrowed: **the Web Dioxus SOS trigger is the primary active transitional path requiring migration**, while the v2/v3 paths are legacy-generation reachability targets and `src/services/emergency_sos.py` requires route-registration verification before it can be classified as unreachable.

## Important security/architecture conclusions

1. **There is already real SOS code, but it is not a canonical production-grade SOS capability.** The current implementations mix transport, storage, wiping, authorization-like behavior, and user-data handling at surface/service level.
2. **The most dangerous existing pattern is success semantics.** The legacy implementations can report emergency dispatch/wipe completion without proving delivery or defining acknowledgement. The canonical contract must distinguish `LOCAL_ONLY`, `QUEUED`, `TRANSMITTING`, `ACCEPTED`, `DELIVERED`, `ACKNOWLEDGED`, `FAILED`, and `UNKNOWN` where applicable.
3. **Global local-storage wiping must not be treated as a generic SOS primitive.** Emergency privacy behavior needs an explicit, documented scope and must not destroy unrelated user data or preserved evidence accidentally.
4. **Location must be purpose-bound and minimized.** GPS/location access is not equivalent to continuous tracking and must follow the existing purpose-bound permission contract.
5. **Camera permission is not face/CV permission. Microphone permission is not transcription/upload permission.** These must remain separate capability decisions.
6. **Mesh/satellite/transport implementations must sit behind provider-neutral transport contracts.** Surfaces must not select providers or directly construct transport clients.
7. **External police/emergency dispatch is a consequential external action.** It requires authorization, explicit user confirmation where appropriate, verified official endpoint/adaptor semantics, and truthful acknowledgement/delivery state.
8. **No new database, object store, Redis dependency, Nostr transport, mesh stack, or AI provider should be introduced by the next SOS implementation step.** First converge the boundary using existing primitives.

## Required next implementation boundary

Build the canonical SOS capability around these existing contracts:

`Surface Adapter → SOS Capability → Safety/Privacy Decision Boundary → Authorization/Consent → Evidence (optional) → Provider-neutral Delivery/Transport Adapter → truthful delivery state`

The SOS capability must remain independently operable from Web, Telegram, Android, iOS, WhatsApp, Messenger, DApp/Web3, and future surfaces. Failure of one surface or transport must not imply failure of the capability as a whole.

## Archive/delete rule

The legacy paths above are **not deleted in this audit**. They remain available as evidence until a dependency/reference audit proves they are no longer needed. Any removal must follow the repository rule: archive first, then delete only after evidence.

## Verification gate before implementation

- [x] Existing SOS implementations located.
- [x] Existing camera/microphone/location/biometric references located.
- [x] Existing authorization and consent primitives identified.
- [x] Existing evidence capability identified.
- [x] Existing privacy/purpose-bound contracts identified.
- [x] No duplicate safety/privacy policy should be introduced.
- [x] Concrete SOS symbol/import reachability traced across current and legacy generations.
- [ ] Verify registration/reachability of legacy `/api/v1/agent/trigger-sos` route.
- [ ] Migrate active Web Dioxus SOS surface to canonical SOS capability.
- [ ] Define the provider-neutral SOS delivery/transport contract.
- [ ] Implement canonical SOS capability and tests.
- [ ] Integrate remaining surfaces independently.
- [ ] Verify external emergency/police adapter semantics before any direct dispatch feature.
