# Civic Action Document Workflow

## Canonical rule

Janavani generates civic-action documents for the citizen to review, correct, print, and/or download. Janavani does **not** email the generated document to the recipient as part of the document-generation capability.

The generated artifact may be PDF or an editable document format supported by the platform (for example DOCX). Submission to an authority is a separate, explicitly user-controlled capability and is not implicit in document generation.

## Workflow

```text
Citizen describes problem
        ↓
Issue understanding / clarification
        ↓
Authority discovery + verification
        ↓
Draft from canonical template
        ↓
Pre-fill verified To / CC details
        ↓
Citizen reviews content + recipients
        ↓
Citizen may correct either
        ↓
Correction captured as a learning signal
        ↓
Verification / moderation gate
        ↓
Generate PDF / editable document
        ↓
Print or download
        ↓
Optional separate submission workflow
```

## Recipient fields

The document editor should support:

- To name, designation, department, postal address, official email when verified;
- CC name, designation, department, postal address, official email when verified;
- source/provenance for recipient data;
- freshness/retrieval timestamp;
- user correction;
- verification status.

Unverified addresses or email addresses must never be presented as verified facts.

## User corrections

A correction must be represented as a structured feedback event, not silently overwrite trusted source data.

```text
Verified source
      ↓
Suggested recipient
      ↓
User correction
      ↓
Correction event
      ↓
Verification queue / corroboration
      ↓
Trusted directory update only after verification
```

A user's correction can immediately affect their current document after review, but it must not automatically become a platform-wide trusted fact.

## Learning

Janavani may learn from corrections only through privacy-preserving, purpose-limited signals. Personal/sensitive case content must not be sent to AI or external learning systems by default. Corrections about public authority metadata may be separated from the citizen's identity and private case data before review.

## AI and Agentic AI

AI may help understand the citizen's description, classify the issue, propose a document structure, improve language, translate, or suggest recipients. AI is optional for the citizen but remains a shared ecosystem capability.

By design and by default, personal and sensitive Case/Evidence data must not be shared with AI/Agentic AI. Only explicitly allow-listed, minimized context may cross the privacy gateway. Agentic AI cannot submit or transmit a consequential action without the applicable authorization and user-confirmation gates.

## No email delivery

Document generation must not expose a generic "email this document" action. Email, if ever supported as a distinct future capability, requires its own contract, destination verification, privacy policy, authorization, audit, and user confirmation. It is not part of this document-generation capability.

## Languages

The document pipeline should preserve structured content separately from rendered language. A canonical semantic representation can be rendered into English and supported Indian languages without duplicating business logic.

Language support should distinguish:

1. UI language;
2. citizen input language;
3. reasoning/normalization language where necessary;
4. document output language.

Translation must preserve names, dates, amounts, addresses, reference numbers, legal citations, and other structured fields exactly unless the user explicitly changes them.

## Completion gate

The workflow is not production-complete until template versioning, authority verification, user editing, correction provenance, PDF/DOCX generation, privacy controls, language QA, print/download QA, and end-to-end tests are verified.
