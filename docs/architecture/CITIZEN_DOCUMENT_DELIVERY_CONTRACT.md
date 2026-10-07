# Janavani Citizen Document Delivery Contract

**Status:** ACTIVE PRODUCT CONTRACT

## Core rule

Janavani does **not** submit petitions, RTI applications, representations, or other citizen documents directly to an authority.

Janavani prepares the citizen's document, presents it for review, generates the final downloadable artifact, and gives the citizen the information needed to send it independently by email or post.

## Supported document outputs

A citizen may request:

- Petition
- RTI application
- Both

Each selected document type is independently rendered as:

- PDF
- DOCX

## Address preparation

Where verified authority data exists, Janavani pre-fills:

- **To:** relevant authority/office name
- postal address
- official email address, when verified
- **CC:** relevant verified contacts where applicable

The citizen's **From** section is deliberately not treated as known by Janavani. The generated document contains explicit fill-in fields for:

- citizen name
- citizen postal address
- citizen email address

The citizen reviews and completes these fields before sending.

## Delivery boundary

The product boundary is:

`Case → Authority discovery → Document generation → Citizen review → Final artifact → Download → Citizen sends by email/post`

There is no product path:

`Case → Janavani → external authority`

## Trust requirements

Janavani must never:

- send the document by email on behalf of the citizen;
- post the document on behalf of the citizen;
- claim that the authority received the document;
- create a government acknowledgement;
- represent an artifact download as submission;
- silently change the authority destination after citizen review.

Janavani may maintain verified authority metadata and show the citizen where the document is intended to be sent.

## RTI-specific note

The official Central Government RTI Online portal supports online filing for covered Central Government public authorities, while stating that State Government public authorities should not be filed through that portal. Janavani therefore should not hard-code a universal “RTI online submission” path; it should generate the citizen-controlled RTI document and clearly identify the appropriate official route when known. citeturn0search6turn0search10
