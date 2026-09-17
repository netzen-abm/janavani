# Janavani Safety & Privacy Decision Boundary

**Status:** Proposed canonical architecture contract  
**Scope:** Safety/SOS and other sensitive device/data capabilities  

## 1. Purpose

This boundary is the shared decision point for purpose-bound access to sensitive capabilities. It prevents a surface, AI component, or device integration from treating a broad permission as blanket authority to collect, process, transmit, or act.

It complements—not replaces—the existing authorization and consent boundaries.

## 2. Decision layers

A request must remain separable into:

1. **Capability authorization** — may this identity invoke the capability?
2. **Purpose-bound access** — is the requested device/data access necessary for the declared purpose?
3. **User choice / consent** — did the user explicitly choose the operation and its material data consequences?
4. **Data policy** — can the minimum required data be used for that purpose?
5. **External action approval** — if the operation has consequential external effects, is the required approval present?

Passing one layer never implies passing the others.

## 3. Canonical outcomes

The boundary exposes four deterministic outcomes:

- `ALLOW` — purpose, authorization and minimization conditions permit access.
- `MINIMIZE` — access cannot proceed until unnecessary collection/data scope is reduced.
- `BLOCK` — the request violates a hard boundary or lacks required authority/choice.
- `REVIEW` — an additional human approval or review step is required.

## 4. Sensitive-resource invariants

### Camera

Camera access is scoped to the declared purpose. Camera access does not authorize face recognition, biometric matching, continuous capture, background capture, or upload.

### Microphone

Microphone access is scoped to the recording purpose. Microphone access does not authorize continuous/background recording, transcription, upload, voice identification, or model training.

### Location

Location is least-precision by default and purpose-bound. Continuous movement history is not permitted by this boundary. Location updates stop when the purpose completes.

### Contacts

Full address-book access is not implied by a request to notify a person. Prefer user-selected recipients or explicitly supplied destinations.

### Files and media

Use scoped file/media selection where the platform permits. Do not infer permission to inspect unrelated files or retain temporary copies beyond the declared purpose.

### Sensors

Sensors are activated only for the declared observation purpose and duration. They do not become a general telemetry stream.

### Biometric processing

Biometric processing is separately scoped. A camera or microphone request must never silently activate face recognition, identity matching, voice identification, watchlists, or public reverse-search behavior.

## 5. Transmission boundary

Local capture/processing and remote transmission are separate decisions.

Remote transmission requires an explicit upload/data-sharing purpose and user choice. Emergency behavior must remain truthful about whether data was locally preserved, queued, transmitted, accepted, delivered, acknowledged, failed, or unknown.

## 6. Consequential actions

Police alerts, complaint/FIR submission, messaging, public publication, or other consequential external actions are not authorized merely because sensitive evidence access was allowed.

They must pass the existing authorization/consent/approval and consequential-operation boundaries. If no verified official intake adapter exists, Janavani must provide an honest manual/export path rather than claim submission.

## 7. Purpose completion and release

The canonical lifecycle is:

**Ask → Explain purpose → Grant → Use → Purpose Complete → Release → Ask Again**

Application-level resource access and temporary handles/state must be released when the purpose completes. Where an operating system does not expose programmatic permission revocation, Janavani must stop the resource/session and honestly treat the grant as inactive for the application workflow; the next use must initiate a fresh purpose explanation and permission flow as required by that platform.

## 8. Emergency safety

The boundary must not make an SOS impossible merely because an optional evidence capability was denied or unavailable. The system should fall back to the safest available path and state exactly what occurred.

The boundary also must not encourage unsafe phone handling while driving. Hands-free/voice interaction may be offered where the platform supports it safely.

## 9. AI and derived evidence

AI may assist with OCR, transcription, classification, summarization, or visual analysis only after the relevant data-access decision permits the operation. AI output is not automatically verified evidence, identity, attribution, or authority.

Derived evidence must remain distinguishable from the original citizen-owned evidence and retain provenance to the extent technically feasible.

## 10. Surface independence

Web, Android, iOS, Telegram, Mini App, WhatsApp, Messenger, and future surfaces must consume this shared boundary rather than implement competing privacy/safety gates.

A failure in one access surface must not become a requirement for another surface to run.

## 11. Non-goals

This boundary does not:

- implement operating-system permission APIs;
- store raw media;
- decide police/legal outcomes;
- identify people from faces or voices;
- create a surveillance/watchlist system;
- authorize arbitrary AI-agent actions;
- create a new database or provider.

Those concerns remain behind their respective canonical contracts and adapters.

## 12. Required negative tests

At minimum, tests must prove that:

- no explicit user choice → `BLOCK`;
- background access → `BLOCK`;
- continuous sensitive access → `BLOCK`;
- remote transmission without explicit upload purpose → `BLOCK`;
- camera does not imply biometric processing → `BLOCK`;
- consequential action without its separate approval path → `REVIEW`/`BLOCK`;
- missing capability authorization → `BLOCK`;
- non-minimized data request → `MINIMIZE`;
- denied optional evidence capability still permits the safest available SOS fallback;
- purpose completion releases application-level access/state;
- a later use requires a fresh purpose/permission flow;
- AI processing is not silently enabled by device permission;
- preserved evidence continues through the canonical Evidence capability and provenance boundary.

## 13. Implementation rule

No second safety/privacy policy engine should be introduced. This boundary must compose with the existing authorization, consent, execution-aware consent, consequential-operation, Evidence, and purpose-bound permission contracts.

Implementation should remain provider-neutral and surface-neutral.
