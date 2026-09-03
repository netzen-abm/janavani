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

## Delivery rule

Generation is not submission.

The document capability may produce PDF and DOCX artifacts for user review,
printing and download. It must not send a government submission merely because
an artifact was generated.

Government delivery requires the separate CivicCase submission lifecycle and
its delivery/acknowledgement evidence.

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
             optional later submission
                    |
             CivicCase submission flow
```

## Required future gates

Before replacing the legacy generation path:

1. resolve `To` from the canonical authority/office capability;
2. preserve verified `To` email and `CC` email as metadata only;
3. allow user correction of document content and destinations;
4. produce deterministic document metadata and references;
5. attach the resulting document reference to the CivicCase;
6. test PDF and DOCX outputs independently;
7. verify no email is sent by document generation;
8. retire legacy generators only after evidence and archive.
