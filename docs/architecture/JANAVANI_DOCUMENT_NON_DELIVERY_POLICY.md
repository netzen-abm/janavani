# JanaVani Document Non-Delivery & Follow-Up Policy

## Canonical rule

**JanaVani generates documents and makes them available for user download.
JanaVani never sends a generated document directly to any external destination.**

JanaVani does not email, post, courier, portal-submit, or otherwise transmit a
generated document on the user's behalf.

JanaVani's document responsibility ends at:

1. generating the document;
2. allowing the user to review and correct it;
3. providing the final PDF or DOCX/Word file for download.

What the user does with the downloaded file is the user's choice and is
outside JanaVani's document-delivery business boundary.

## User-controlled delivery

After download, the user may independently:

- send the PDF/DOCX by their own email;
- print it and send it through a post office;
- print it and deliver it physically;
- use another delivery method of their own choice.

JanaVani does not perform or initiate those delivery actions.

## Follow-up is a separate JanaVani capability

**Follow-up support is allowed and is separate from document delivery.**

After a document is generated/downloaded, JanaVani may remind the user about
user-selected follow-up activities, for example:

- review the document;
- download or print the document;
- send the document themselves;
- check whether they received a response;
- follow up with the authority;
- prepare a subsequent representation, appeal, or reminder;
- record an outcome reported by the user.

A reminder is not a transmission. JanaVani must never interpret a reminder as
proof that the user actually sent the document.

## Product boundary

```text
Citizen input
    |
    v
JanaVani Case + Authority + Document capabilities
    |
    v
Generate PDF / DOCX
    |
    v
User reviews / corrects
    |
    v
DOWNLOAD
    |
    +----> User sends email themselves
    |
    +----> User prints and posts themselves
    |
    +----> User prints and delivers themselves
    |
    v
Optional JanaVani follow-up reminder
    |
    v
User reports / records outcome
```

The delivery actions remain outside JanaVani's execution boundary.

## Prohibited behavior

No JanaVani surface or service may:

- send the generated document by email;
- call an SMTP/email delivery service to transmit the document;
- submit the document to a government portal automatically;
- send the document to an office's email address;
- mail or courier the document on the user's behalf;
- automatically transmit the document through Telegram, WhatsApp, or another
  channel to the government/authority as a submission;
- interpret a generated/downloaded artifact as a government submission;
- claim government receipt or acknowledgement merely because a document was
  generated or downloaded;
- claim that a user completed delivery merely because a reminder was issued.

## Address and email handling

The document may contain verified `To` and `CC` address/email information so
the user can review it and use it for their own delivery. This information is
**document metadata, not a delivery instruction to JanaVani**.

The user must be able to correct the document and destination details before
download.

## Lifecycle boundary

`DOCUMENT_GENERATED` and `DOCUMENT_DOWNLOADED` are artifact events.

They do **not** mean:

- `SUBMITTED`;
- `DELIVERED`;
- `ACKNOWLEDGED`; or
- `RECEIVED` by an authority.

A follow-up reminder likewise does not create evidence of submission or
receipt. Only user-provided evidence or a separately verified future capability
may establish such facts.

## Follow-up reminders must remain user-controlled

Follow-up reminders may be scheduled only according to the user's selected
preference or an explicit workflow choice. They should remind the user of an
activity; they must not perform that activity automatically.

## Enforcement

Document-generation tests must verify that the generation path has no email,
postal, courier, portal-submission, or other external-delivery side effect.
Follow-up tests must verify that reminders do not mutate delivery truth or
fabricate submission/acknowledgement evidence.

Any future transport integration that could transmit documents must be
rejected unless this policy is explicitly changed at the product-governance
level.
