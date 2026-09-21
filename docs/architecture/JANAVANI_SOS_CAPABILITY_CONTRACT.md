# Janavani SOS Capability Contract

**Status:** Architectural contract — implementation in bounded stages
**Date:** 2026-09-16

## 1. Purpose

Define one canonical, surface-independent SOS capability for personal safety and emergency assistance.

SOS is a capability, not a Web, Telegram, Android, iOS, WhatsApp, Messenger, DApp/Web3, or transport implementation.

## 2. Canonical flow

`Surface Adapter → SOS Capability → Safety/Privacy Decision → Authorization/Consent → Evidence (optional) → Provider-neutral Delivery/Transport → truthful delivery state`

The SOS capability must remain independently operable when any individual access surface or transport provider is unavailable.

## 3. Scope

The capability may coordinate:

- a citizen-triggered emergency event;
- optional trusted-contact notification according to user configuration;
- optional location sharing according to the existing purpose-bound location contract;
- optional photo, video, or audio evidence through the canonical Evidence capability;
- optional delivery through an available provider-neutral transport;
- a truthful delivery/acknowledgement state for each delivery attempt;
- preparation of information that a user may use for an emergency/police complaint.

## 4. Non-goals

The SOS capability must not:

- directly construct Redis, Nostr, Reticulum, satellite, HTTP, messaging, or other provider clients;
- choose concrete transport providers at the surface layer;
- silently upload evidence or location;
- silently enable camera, microphone, continuous location, contacts, or biometric processing;
- globally wipe unrelated browser/device storage;
- claim police/emergency delivery from an HTTP success, locally generated identifier, or provider attempt alone;
- autonomously determine criminality, guilt, identity, or legal outcome;
- submit consequential police/emergency actions without the applicable authorization, consent, explicit confirmation, and verified official-adapter requirements;
- create a second authorization, consent, privacy, evidence, or device-permission engine.

## 5. SOS request boundary

A request contains only the minimum information needed for the requested operation. The capability must distinguish:

- incident type/context supplied by the citizen;
- evidence references, when the citizen has deliberately selected evidence;
- location, only when the purpose and sharing mode permit it;
- configured recipients/destinations;
- requested delivery channels;
- request/incident identifiers that are opaque and non-identifying.

Raw media remains governed by the canonical citizen-evidence and safety-audio contracts.

## 6. Delivery state

The canonical SOS capability uses truthful per-attempt delivery states:

- `LOCAL_ONLY` — SOS information exists locally and has not entered a delivery attempt.
- `QUEUED` — a delivery attempt is waiting for an available transport.
- `TRANSMITTING` — a transport attempt is in progress.
- `ACCEPTED` — the selected destination/provider accepted the payload for handling; this is not proof of end-recipient receipt.
- `DELIVERED` — the transport has authoritative evidence of delivery to the intended destination.
- `ACKNOWLEDGED` — the intended recipient/destination has provided an acknowledgement reference.
- `FAILED` — the delivery attempt failed with a known failure reason.
- `UNKNOWN` — the system cannot establish the delivery state truthfully.

`SENT`, `RECEIVED`, and other legacy terminology may be mapped at adapters, but must not be treated as stronger evidence than the underlying provider semantics justify.

## 7. Provider-neutral delivery contract

A transport adapter receives a normalized delivery request and returns a delivery result. The adapter is responsible for provider-specific mechanics; the SOS capability owns orchestration and truthful state interpretation.

Conceptual contract:

```text
DeliveryRequest
  delivery_id
  sos_id
  destination_ref
  payload_ref
  transport_kind
  requested_at

DeliveryResult
  delivery_id
  transport_kind
  state
  provider_reference|null
  acknowledgement_reference|null
  attempted_at
  error_code|null
```

A provider adapter must not persist directly into a surface-owned store. Storage remains behind the shared repository/provider boundary.

## 8. Transport independence

Supported transport kinds are replaceable implementations. The initial contract may represent:

`INTERNET | RETICULUM | LORA | MESHTASTIC | SATELLITE | LOCAL | OTHER`

Availability of a transport must never be represented as successful delivery merely because the provider object was constructed or an attempt returned a local identifier.

Multiple attempts may coexist. Each attempt has its own state and evidence.

## 9. Privacy and purpose binding

Device access follows the canonical lifecycle:

`Ask → Explain purpose → Grant → Use → Purpose Complete → Release → Ask Again`

SOS does not grant permanent access to camera, microphone, location, contacts, files, sensors, or biometric processing.

Location sharing must follow the existing emergency location-sharing modes and minimization rules. Camera access does not grant face/CV processing. Microphone access does not grant transcription, upload, voice identification, or training.

## 10. Evidence integration

Evidence is optional unless the user chooses to capture or attach it. When used:

`capture → privacy/sensitive gate → user review → explicit upload decision → EvidenceCapability → provenance/repository`

The SOS capability must reference evidence; it must not create a parallel evidence store.

Evidence remains distinguishable from allegations, model output, and verified findings.

## 11. Consequential emergency/police actions

A direct external emergency or police action is a consequential operation. It requires:

1. canonical authorization;
2. applicable consent/user-choice checks;
3. explicit confirmation where the action contract requires it;
4. a verified official destination/adapter;
5. provider-specific acknowledgement semantics;
6. truthful state reporting.

If no verified official adapter is available, the capability must provide a safe alternative such as a user-reviewed complaint/FIR draft or downloadable/shareable evidence package, rather than claiming submission.

## 12. Failure and fallback behavior

Failure isolation is mandatory:

- Web failure must not disable Telegram or another surface.
- One transport failure must not imply all transports failed.
- Offline operation may preserve a local SOS and queue it, but must not claim delivery.
- Missing location permission must not silently become continuous tracking.
- Denied evidence permission must not prevent the safest available SOS path.
- Missing microphone/camera/biometric capability must not block the emergency path when an alternative exists.
- Unknown provider state must remain `UNKNOWN`, not be upgraded to success.

## 13. Security invariants

- No hard-coded credentials or provider endpoints.
- No direct provider construction outside approved composition roots/adapters.
- No global local-storage wipe as a generic SOS action.
- No silent transmission of personal/sensitive data.
- No public face search, watchlist, or identity matching as part of SOS.
- No autonomous accusations or legal conclusions.
- No false delivery/acknowledgement claims.
- No cross-surface runtime ownership.

## 14. Implementation sequence

1. Reuse the existing Safety/Privacy Decision Boundary from PR #178 after review/merge.
2. Implement the provider-neutral SOS request/result model and capability orchestration.
3. Implement deterministic negative/failure tests before concrete transports.
4. Integrate the Web Dioxus surface as an adapter without importing legacy SOS transport logic.
5. Verify trusted-contact delivery semantics.
6. Add concrete transport adapters individually, only when provider contracts and credentials are verified.
7. Evaluate official emergency/police adapters separately as consequential operations.
8. After reference/dependency evidence is complete, archive legacy SOS generations. Delete only after archival evidence.

## 15. Required tests

The canonical implementation must test at minimum:

- missing authorization → denied;
- missing explicit user choice → denied;
- background/continuous device access → denied;
- remote transmission without explicit upload purpose → denied;
- biometric processing without separate scope → denied;
- consequential action without required approval → review/denied according to the canonical policy;
- local SOS without transport → `LOCAL_ONLY`;
- queued offline delivery → `QUEUED`, never `DELIVERED`;
- provider acceptance → `ACCEPTED`, never automatically `DELIVERED`;
- explicit acknowledgement → `ACKNOWLEDGED`;
- provider failure → `FAILED`;
- indeterminate provider result → `UNKNOWN`;
- one failed transport leaves other eligible transports independent;
- no global local-storage wipe occurs as a generic SOS side effect;
- evidence references remain traceable through the canonical Evidence capability.

## 16. Ownership

**Canonical capability owner:** SOS capability layer.

**Policy owners reused:** Authorization, Consent, Safety/Privacy Decision Boundary, Purpose-Bound Permission.

**Evidence owner reused:** Evidence capability/repository.

**Transport owner:** Provider-neutral delivery/transport contract plus concrete adapters.

**Surface owner:** Each access surface only adapts user interaction and normalized identity/context into the shared capability.

## 17. Convergence rule

Existing SOS implementations are migration sources, not competing canonical owners. No new SOS feature should be added to:

- `src/services/emergency_sos.py`;
- `janavani_v2/src/sos.rs`;
- `src/web_dioxus/src/sos_interface.rs`;
- legacy v3 transport modules.

They remain subject to the repository archive-first rule until dependency/reference evidence supports archival.


## 2026-09-21 convergence evidence

The former `src/services/emergency_sos.py` implementation has been archived after establishing and testing explicit canonical boundaries for transient-data destruction and credential/session revocation. Emergency delivery remains behind the existing provider-neutral `SOSDeliveryAdapter` contract. The legacy implementation is no longer an active runtime owner.
