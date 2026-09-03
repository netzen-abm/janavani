# Canonical Document Capability

## Status

Implemented contract; migration from legacy generators remains in progress.

## Purpose

Janavani documents are reusable capability outputs, not Telegram-specific files.
The same document draft must be usable by Web, Android, iOS, DApp, Telegram,
WhatsApp, Messenger and future adapters.

## Contract

`src/documents/document_contract.py` defines `DocumentDraft` and `DocumentParty`.
A draft carries:

- document ID
- case ID
- document type
- date
- subject
- body
- verified destination (`To`)
- optional `CC` destinations
- optional sender
- optional legal ground

Destination email addresses are metadata for the document and do not imply
email submission.

## Delivery boundary

Generation is not submission, and JanaVani does not send or submit the generated
document on the user's behalf.

The document capability may produce PDF and DOCX artifacts for user review,
printing and download. After the user downloads the artifact, any physical or
electronic delivery, filing, emailing, posting, hand delivery, portal upload,
or other external action is outside JanaVani's business boundary.

JanaVani may retain case/document state and provide user-controlled reminders,
follow-up guidance, or preparation of a subsequent document according to the
matter and applicable procedure. It does not execute the external action.

The lifecycle must keep these states distinct:

`GENERATED != USER_APPROVED != DOWNLOADED != SENT_BY_USER != DELIVERED != RECEIVED != ACKNOWLEDGED`

JanaVani must never fabricate `SENT_BY_USER`, `DELIVERED`, `RECEIVED`, or
`ACKNOWLEDGED` from artifact generation or download telemetry.

## Migration rule

Existing builders and generators remain compatibility implementations until
consumer inventory, output comparison, regression tests and migration evidence
are complete. No legacy document generator is deleted solely because this
contract exists.

## Target architecture

```text
CivicCase + Authority + Citizen + Evidence
                    |
                    v
             DocumentDraft
                    |
          +---------+---------+
          |                   |
         PDF                 DOCX
          |                   |
          +---------+---------+
                    v
            User review / print / download
                    |
          user performs external action
                    |
             outside JanaVani
                    |
       JanaVani may remind / guide / prepare next step
```

## Required future gates

Before replacing the legacy generation path:

1. resolve `To` from the canonical authority/office capability;
2. preserve verified `To` email and `CC` email as metadata only;
3. allow user correction of document content and destinations;
4. produce deterministic document metadata and references;
5. attach the resulting document reference to the CivicCase;
6. test PDF and DOCX outputs independently;
7. verify document generation contains no submission or dispatch path;
8. verify external delivery states are never inferred from generation/download;
9. retire legacy generators only after evidence and archive.
