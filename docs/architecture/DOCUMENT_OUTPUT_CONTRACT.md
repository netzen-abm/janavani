# Janavani — Final Document Output Contract

## Status
Canonical product and engineering requirement.

## Principle
Janavani creates a single format-neutral structured document model first. The **user decides the final output format**.

The supported user choices are:

- **PDF** → final artifact is `.pdf`;
- **Document** → final artifact is an editable Microsoft Word `.docx` document.

"Document" is the product-language choice presented to the user. `docx` is the implementation format and file extension.

## Required flow

```text
User describes civic need
        ↓
Shared Case / Document capability
        ↓
Structured Document Model
        ↓
Quality + provenance + safety checks
        ↓
Ask / record user's output choice
        ↓
 ┌───────────────┬────────────────┐
 │ PDF           │ Document       │
 │ renderer      │ renderer       │
 │ .pdf          │ .docx          │
 └───────────────┴────────────────┘
        ↓
Final user-selected artifact
```

## User agency
The platform MUST NOT silently choose PDF or Document when the product workflow requires a final downloadable artifact. The user choice is part of the document-generation request.

A UI, Telegram bot, mobile client, or other access surface may present the choice, but the choice is passed into the shared document capability. Format-specific business logic must not live in the access surface.

## Canonical API semantics

```text
output_format = "pdf"
    → PDF artifact

output_format = "document"
    → editable DOCX artifact
```

`doc` and `docx` may be accepted as compatibility aliases for `document`, but new product surfaces should present **PDF** and **Document**.

## Content integrity
Both formats MUST originate from the same structured document payload. The platform must not generate materially different legal/civic content merely because the user selected PDF versus Document.

Differences may be limited to renderer-specific presentation, pagination, typography, metadata, and format capabilities.

## Reusability
The output-format contract is shared infrastructure and is available to:

- WebApp;
- Telegram Bot;
- Telegram Mini App;
- Android/iOS;
- WhatsApp/Messenger;
- DApp;
- future access surfaces.

No access surface owns the document format policy.

## Quality requirements
Before rendering, the shared pipeline should be able to enforce the same:

- document type;
- user-supplied facts;
- authority/source references;
- provenance;
- jurisdiction;
- verification status;
- privacy/safety constraints;
- user corrections;
- document quality checks.

## Failure behavior
If the selected renderer is unavailable, Janavani MUST NOT silently substitute another format. It should report that the selected format is temporarily unavailable and offer another format only as an explicit user choice.

## Definition of done
The document capability is complete when:

1. one structured payload can feed both renderers;
2. the user's output choice is explicit;
3. PDF and Document rendering are independently testable;
4. format-specific logic remains behind the shared renderer boundary;
5. access surfaces do not duplicate document-generation logic;
6. failures do not silently change the user's selected format;
7. provenance, privacy and safety survive both output paths.
