# 🇮🇳 JANAVANI
# PRIVACY ARCHITECTURE

Version 2.0

---

## 1. Non-Negotiable Privacy Boundary

**JanaVani does not build a personal-data repository.**

The default architecture is **device-first, privacy-preserving, and capability-independent**.

Personal data belongs to the citizen and remains on the citizen's device whenever technically possible.

JanaVani services must not require a central personal-data store, user profiling database, advertising identity graph, or behavioural surveillance layer.

If a capability genuinely requires data to leave the device, the transfer must be:

1. explicitly necessary for the selected capability;
2. visible to the user before transmission;
3. encrypted in transit;
4. minimized to the smallest useful payload;
5. directed only to the selected destination/capability;
6. independently disposable after completion where retention is not required;
7. designed so failure of that capability does not expose or disable unrelated capabilities.

---

## 2. Privacy by Design and by Default

Privacy is not an optional mode.

Privacy is the baseline architecture of JanaVani.

Users may **opt into additional capabilities**, including decentralized networks, Web3/DApp functions, AI services, messaging integrations, mesh transports, and external submissions. Opting into a capability must not silently opt the citizen into unrelated data collection.

The governing principle is:

> **Capability opt-in is not data-collection consent.**

Every capability must separately explain what data it needs, where it goes, why it goes there, and how long it is retained.

---

## 3. Data Ownership Model

### Citizen device — primary data domain

The user's device is the normal location for:

- drafts;
- complaints and grievance records;
- generated letters;
- attachments;
- evidence;
- identity information;
- addresses and contact details;
- preferences;
- local cryptographic keys;
- optional wallet credentials;
- offline application state.

Where local persistence is used, sensitive information must be encrypted at rest using platform-appropriate secure storage.

### JanaVani infrastructure — capability execution domain

JanaVani infrastructure should normally process only what is necessary to execute an explicitly selected capability.

The infrastructure must not become a permanent personal-data vault.

Operational telemetry should be minimized and must not be used to reconstruct individual citizen profiles.

### External destination — citizen-selected submission domain

When a citizen chooses to send a document to a government office, messaging service, AI provider, decentralized relay, blockchain, or other external destination, the application must treat that as a distinct capability boundary.

The destination receives only the payload required for that action.

---

## 4. Personal Data Rule

JanaVani must **not permanently store personal data on its own servers by default**.

Examples include:

- name;
- postal address;
- telephone number;
- email address;
- precise location history;
- government identifiers;
- identity documents;
- biometric information;
- private keys or wallet seed material;
- private communications;
- personal attachments.

If an external authority or service requires such information, it should be assembled locally on the user's device and transmitted only when the user selects and authorizes that action.

JanaVani must not silently copy that information into an unrelated internal database.

---

## 5. Identity Modes

Identity is a capability input, not a prerequisite for using JanaVani.

### Anonymous

No personal identity is attached unless the selected destination legally requires it.

### Name only

Only the citizen's chosen name is inserted into the selected document.

### Full identity

The citizen may locally provide the minimum required contact information, such as:

- name;
- postal address;
- phone;
- email.

These values remain local unless the citizen explicitly chooses a transmission capability.

---

## 6. Sensitive Data Never Requested by Default

JanaVani must not request the following merely for personalization, analytics, ranking, or convenience:

- Aadhaar number;
- PAN;
- date of birth;
- religion;
- caste;
- gender;
- income;
- political preference;
- biometric information;
- continuous location history.

A capability may request a specific item only where the selected legal/administrative workflow genuinely requires it. The reason must be presented to the citizen.

---

## 7. Encryption Boundary

Any personal or otherwise sensitive payload leaving the device must use authenticated encryption appropriate to the selected transport.

Minimum requirements:

- TLS for conventional network APIs;
- end-to-end encryption where the selected protocol supports it;
- authenticated encryption for application-level sensitive payloads where required;
- cryptographic keys kept outside ordinary application logs;
- no secrets embedded in client source code;
- no plaintext personal data in telemetry, crash reports, URLs, analytics events, or debug logs.

Encryption does **not** make unnecessary collection acceptable. Data minimization remains mandatory.

---

## 8. Capability Isolation

Every major JanaVani capability is an independent boundary:

- Android client;
- iOS client;
- Web application;
- DApp/Web3;
- Telegram application;
- Telegram Mini App;
- WhatsApp integration;
- Messenger integration;
- Nostr;
- Nym Mixnet;
- Reticulum Mesh;
- Freenet;
- blockchain/ZKP;
- AI/LLM/SLM;
- Agentic AI;
- RAG;
- VLM;
- LAM;
- MoE;
- MLM;
- SAM;
- OCR;
- computer vision.

Failure, compromise, outage, or refusal by one capability must not require personal-data replication into another capability and must not prevent unrelated capabilities from operating.

---

## 9. User-Controlled Capability Selection

The user decides which capabilities are active.

Examples:

- A citizen may use the Web application without Web3.
- A citizen may use the DApp without AI.
- A citizen may use AI locally without sending data to a cloud model.
- A citizen may use Freenet without using a conventional backend.
- A citizen may submit a document through email without enabling a blockchain wallet.
- A citizen may use an Android client without enabling messaging integrations.

No capability may silently activate another capability or inherit its data permissions.

---

## 10. Local-First Workflow

Preferred workflow:

```text
Citizen input
    ↓
Local processing / local validation
    ↓
Local encrypted storage (if the citizen chooses to save)
    ↓
Capability selection
    ↓
Explicit transmission decision
    ↓
Encrypted transport
    ↓
Selected destination
```

Where a workflow can be completed locally, it should not require a server round trip.

---

## 11. Data Retention

The default JanaVani retention rule is:

> **If JanaVani does not need to retain data to provide the selected capability, JanaVani should not retain it.**

Temporary processing data should be deleted as soon as operationally possible.

A capability that requires external legal or administrative retention is responsible for clearly identifying that external retention boundary to the citizen.

---

## 12. Anonymous Public Accountability Data

JanaVani may publish or aggregate non-personal civic information such as:

- complaint counts;
- department trends;
- district-level trends;
- public-service performance indicators;
- office/service ratings;
- bill and policy analysis;
- publicly available government claims and evidence.

Such datasets must be designed to prevent re-identification of individual citizens.

---

## 13. Privacy Review Gate for Every New Feature

Every new feature must answer:

1. Does it require personal data?
2. Can it work without personal data?
3. Can processing happen locally?
4. What exact data leaves the device?
5. Is transmission explicitly authorized?
6. Is the payload encrypted?
7. Where is the destination?
8. How long is it retained?
9. Can the citizen delete the local copy?
10. Does failure of this feature affect unrelated capabilities?

If these questions cannot be answered clearly, the feature is not ready for integration.

---

## 14. Architectural Principle

JanaVani exists to empower citizens, not to profile them.

The platform should progressively move computation, storage, identity control, cryptographic authority, and decision control toward the citizen device wherever practical.

**Privacy by design. Privacy by default. Data minimization by architecture. Capability isolation by design. Citizen control by default.**
