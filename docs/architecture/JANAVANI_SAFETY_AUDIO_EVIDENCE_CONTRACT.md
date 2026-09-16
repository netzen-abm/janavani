# JANAVANI Safety Audio Evidence Contract

**Status:** Proposed canonical capability contract
**Scope:** JNV-SOS-AUDIO-EVIDENCE

## 1. Purpose

Provide a fast, privacy-preserving way for a person in an unsafe situation to preserve a short audio record when taking a photograph or video is impractical, unsafe, or impossible.

Audio evidence is an evidence capability attached to a safety incident. It is not a prerequisite for SOS dispatch and must not require AI, cloud storage, or continuous connectivity.

## 2. Core principle

**Record locally first. Share only what the user chooses and what the selected emergency action requires.**

Microphone permission is not evidence-upload consent.

An SOS trigger is not, by itself, consent to upload an audio recording.

## 3. Emergency sequence

```text
Danger / unsafe situation
        |
        +--> SOS / emergency action --------------------+
        |                                                |
        +--> Optional audio evidence                    |
                |                                       |
                +--> local recording                    |
                +--> user review                        |
                +--> optional minimisation/transcript   |
                +--> explicit preservation/share ------>|
                                                        v
                                                  Incident Case
```

The emergency path must remain available if audio recording, transcription, AI, storage, or network delivery fails.

## 4. Capture

The capability may capture:

- short user-initiated audio;
- capture timestamp;
- incident category selected by the user;
- optional user description;
- optional location appropriate to the selected emergency action;
- evidence hash/provenance metadata when preservation is enabled.

No background or continuous recording by default.

Do not encourage a person who is driving to handle a phone. Where the platform permits, provide hands-free or voice-access initiation and safe stopping behavior.

## 5. Location

Location is purpose-bound.

- Emergency dispatch may require location.
- Evidence preservation does not automatically require precise location.
- Precise location must not be retained merely because an audio file exists.
- Use the minimum precision necessary for the declared action.
- Do not create an unrestricted historical movement database.

## 6. Privacy

Treat audio as high-risk incident evidence because it may contain voices, conversations, background locations, names, vehicle identifiers and other personal information.

Apply:

- local-first storage;
- explicit microphone permission;
- explicit recording state visible to the user where platform rules permit;
- explicit share/upload decision;
- metadata minimisation;
- encryption at rest and in transit when remote storage/transmission is used;
- purpose-bound access control;
- retention limits;
- auditable evidence access;
- no unrelated analytics or model training from incident audio without a separate lawful capability and explicit permission where required.

## 7. Transcription and AI

Transcription is optional assistance, not the source of truth.

If enabled:

- prefer on-device/local processing where feasible;
- clearly label machine-generated transcription;
- preserve the original recording independently when the user chooses evidence preservation;
- do not silently replace the recording with a transcript;
- allow manual correction/annotation;
- do not treat an AI transcript as a verified verbatim record;
- AI failure must not block evidence preservation or SOS.

## 8. Evidence integrity

When the user chooses preservation, create an evidence record using the existing Evidence capability rather than inventing a parallel storage system.

The evidence record should identify, where available:

- evidence identifier;
- media type;
- capture/receipt timestamps;
- hash;
- provenance;
- transformations such as trimming, transcription or redaction;
- verification state;
- access/retention policy references.

Derived material must remain distinguishable from the original recording.

## 9. Incident context

Useful structured context may include:

- incident category;
- approximate location or emergency location;
- date/time;
- direction of travel where relevant and voluntarily supplied;
- vehicle type/description where relevant;
- concise user narrative;
- whether immediate danger continues;
- selected evidence references;
- emergency destination and delivery state.

Collect only information needed for the selected capability.

## 10. Police and emergency action

Audio evidence may be associated with an emergency alert or complaint package, but evidence capture must not falsely imply police receipt.

Emergency alerting should use a verified official emergency/police adapter where available.

Complaint/FIR-oriented drafting may use the structured incident facts and selected evidence references.

Electronic police submission is permitted only through a verified official intake adapter with explicit user confirmation and sufficient acknowledgement semantics. Otherwise provide an editable complaint and PDF/DOCX export for independent submission.

## 11. Delivery states

Audio evidence and emergency messages use truthful states such as:

`LOCAL_ONLY`
`QUEUED`
`TRANSMITTING`
`ACCEPTED`
`DELIVERED`
`ACKNOWLEDGED`
`FAILED`
`UNKNOWN`

A successful local save is not remote delivery.

An HTTP success response alone is not proof that police received the evidence.

## 12. Face/CV relationship

Audio and face/CV are separate capabilities.

A user may record audio without enabling any visual processing.

Face/CV must never be automatically activated because an SOS or audio recording exists.

## 13. Abuse prevention

The capability must not provide:

- covert continuous surveillance;
- unrestricted recording of unrelated people;
- public publication of private recordings by default;
- identity inference from voices without a separately justified capability;
- stalking or individual movement tracking;
- automated accusation generation;
- fabricated emergency/police delivery claims.

The product should warn users about applicable recording/privacy laws and local circumstances where appropriate, without obstructing a genuine emergency safety path.

## 14. Failure behavior

If microphone access fails:

- SOS remains available;
- photo/video or structured incident evidence may remain available;
- user receives a truthful explanation.

If network fails:

- local evidence remains available;
- local case/draft remains available where supported;
- queued delivery is explicit;
- no delivery claim is made.

If AI fails:

- original audio remains available;
- manual description remains available;
- SOS remains available.

If remote storage fails:

- preserve local state where possible;
- do not claim remote preservation.

## 15. Implementation boundary

Reuse:

- `JNV-SOS-PERSONAL`
- `JNV-SOS-DELIVERY`
- `JNV-SOS-EVIDENCE`
- `JNV-EVIDENCE-CAPTURE`
- `JNV-EVIDENCE-PROVENANCE`
- existing Case/Submission/Consent capabilities where appropriate.

Do not create a separate audio database, provider-specific surface implementation, or mandatory AI service as part of this contract.

## 16. Completion gates

Before production status:

1. microphone permission and recording-consent tests;
2. local-only capture tests;
3. upload-consent separation tests;
4. metadata minimisation tests;
5. truthful delivery-state tests;
6. network/AI/storage failure tests;
7. driving-safety UX tests;
8. access-control and retention tests;
9. provenance/hash verification tests;
10. negative tests proving audio evidence cannot trigger automatic accusation, identity inference, or false police-delivery state.
