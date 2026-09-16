# JANAVANI Purpose-Bound Permission Lifecycle Contract

**Status:** Proposed canonical cross-capability contract

## 1. Principle

Janavani must treat device permissions as **temporary capability grants tied to a declared purpose**, not as permanent access rights.

> **Ask → Explain purpose → Use → Finish → Release → Ask again when needed.**

Granting camera, microphone, location, contacts, files, Bluetooth, notification, motion/sensor or other device access must never be interpreted as blanket consent for future unrelated use.

## 2. Purpose-bound permission

Before requesting a sensitive device capability, the product must explain:

- what capability is requested;
- the immediate purpose;
- what data will be accessed;
- whether processing is local or remote;
- whether anything will be retained or transmitted;
- how the user can cancel or decline.

The request must be made as close as practical to the moment the capability is needed.

## 3. Lifecycle

```text
NOT NEEDED
    ↓
PURPOSE DECLARED
    ↓
USER CONSENT / PLATFORM GRANT
    ↓
ACTIVE USE
    ↓
PURPOSE COMPLETE
    ↓
RELEASE / STOP / DISABLE
    ↓
NOT NEEDED

Future use → new purpose → new consent/grant as required
```

The application must not keep a capability active merely because it was previously granted.

## 4. Important platform limitation

Janavani cannot unilaterally revoke an operating-system permission in every platform.

Where the OS exposes a revocation API, Janavani should release/revoke access as permitted.

Where the OS does not permit application-level revocation, Janavani must immediately stop using the resource, close the relevant session/stream, clear temporary handles/state, and mark the capability **inactive**. The next use must initiate a fresh in-app purpose explanation and, where the platform requires it, direct the user to the OS permission control.

Therefore the contract is **application-level automatic release**, with OS-level revocation used where technically and legally supported.

## 5. Camera

Examples:

- Evidence capture starts → request camera access for the declared incident purpose.
- Capture ends → stop camera session immediately.
- No background camera access.
- A later capture requires a new purpose-bound activation.
- Camera permission must not imply face/CV processing permission.

## 6. Microphone / audio

- Request microphone access only when recording is requested.
- Stop the recording stream when the recording purpose ends.
- No continuous/background recording by default.
- A later recording requires a new purpose-bound activation.
- Microphone permission does not imply upload, transcription, voice identification or model-training consent.

## 7. Location

Location should use the least precise mode sufficient for the selected action.

Examples:

- Emergency dispatch may request current precise location when necessary.
- Evidence metadata may use approximate location when sufficient.
- After the location-dependent operation finishes, stop location updates.
- Do not retain continuous location history merely because location permission was granted.
- A later location-dependent action requests/activates location again according to platform controls.

## 8. Contacts / address book

Contacts are particularly sensitive and should be treated as exceptional.

- Do not request address-book access merely to make SOS convenient.
- Prefer user-selected recipients or explicit contact selection through platform mechanisms where possible.
- Do not bulk-import contacts when a single recipient is sufficient.
- Do not retain an address book copy merely because access was granted.
- Release contact access after the purpose is complete.
- A later operation requiring contacts initiates a new purpose-bound request.

## 9. Files / media library

Prefer platform-scoped file/photo pickers that give access only to user-selected items.

Do not request broad library access when a single selected file is sufficient.

After processing/upload/preservation completes, discard unnecessary temporary copies and handles according to retention policy.

## 10. Bluetooth, nearby devices and sensors

Apply the same rule to Bluetooth, nearby-device, motion, accelerometer, gyroscope and other sensor access:

- request only for a declared feature;
- activate only while required;
- stop scanning/collection when the purpose ends;
- do not retain unnecessary telemetry;
- require a new activation for a later purpose.

## 11. Emergency exception

Emergency safety must not be defeated by an overcomplicated permission flow.

If a user has not granted a capability, Janavani must provide the safest available alternative rather than pretending it can access unavailable data.

For example:

- no microphone → SOS message/location path may remain available;
- no camera → audio or structured incident report may remain available;
- no location → user can provide location manually where feasible;
- no contacts → configured emergency endpoint or manual recipient path may remain available.

An emergency trigger must never silently expand unrelated permissions.

## 12. User-visible session state

For sensitive capabilities, the application should maintain a simple state model:

`NOT_REQUESTED`
`PURPOSE_PRESENTED`
`GRANTED`
`ACTIVE`
`PURPOSE_COMPLETE`
`RELEASED`
`DENIED`
`UNAVAILABLE`

The UI should make it clear when a sensitive resource is actively being used.

## 13. Data minimisation

Permission lifecycle and data lifecycle are separate controls.

Stopping camera/microphone/location access does not automatically justify retaining everything already collected.

At purpose completion:

1. stop the device resource;
2. minimise temporary data;
3. apply the declared retention rule;
4. preserve only evidence the user explicitly chose to preserve;
5. retain provenance necessary for preserved evidence;
6. discard unrelated data where technically possible.

## 14. AI and derived processing

Permission to access a device resource does not automatically grant permission to send that data to an AI provider.

Separate activation/consent is required for higher-risk processing such as:

- face recognition or identity matching;
- voice identification;
- cloud transcription;
- cloud computer vision;
- model training or secondary analytics.

Local/on-device processing should be preferred where feasible for sensitive emergency evidence.

## 15. Safety against misuse

The implementation must prevent a capability from silently becoming a surveillance channel.

Prohibited defaults include:

- continuous background recording;
- continuous location tracking without an independently justified feature and user control;
- bulk contact harvesting;
- silent camera activation;
- silent microphone activation;
- unrelated secondary use of captured media;
- automatic face/voice identification;
- creation of personal movement histories from emergency data.

## 16. Cross-surface rule

The contract applies equally to Web, Android, iOS, Telegram/Mini App, WhatsApp, Messenger and future surfaces where the underlying platform supports the capability.

Surface adapters may implement platform-specific permission mechanics, but they must not weaken the canonical purpose-bound policy.

## 17. Verification requirements

Before a sensitive device capability is marked production-ready, tests must demonstrate:

1. permission is requested only for a declared purpose;
2. refusal does not break unrelated emergency functionality;
3. active use stops when the purpose ends;
4. no background resource remains active after completion;
5. later use requires a new purpose-bound activation;
6. camera permission cannot activate face/CV automatically;
7. microphone permission cannot activate transcription/upload automatically;
8. location permission cannot create continuous tracking automatically;
9. contact permission cannot trigger bulk import automatically;
10. OS limitations on revocation are handled honestly;
11. temporary data is minimised after completion;
12. preserved evidence remains subject to Evidence/Provenance policy;
13. emergency fallback paths remain functional;
14. logs do not expose sensitive media or unnecessary personal data.

## 18. Architectural relationship

This contract is a cross-capability policy boundary, not a replacement for platform permission APIs.

```text
Surface Adapter
      ↓
Purpose-Bound Permission Policy
      ↓
Platform Permission / Resource Session
      ↓
Capability
      ↓
Evidence / SOS / other shared capability
      ↓
Purpose Complete
      ↓
Resource Release + Data Minimisation
```

The canonical policy must remain provider- and surface-neutral.
