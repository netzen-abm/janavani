# JanaVani Document Non-Delivery Policy

## Canonical rule

**JanaVani will never send a generated document directly to any government,
official, department, office, representative, email address, postal address,
or other external destination.**

JanaVani's responsibility ends at generating the document and making the
artifact available to the user.

## User-controlled delivery

After reviewing the generated document, the user chooses how to deliver it:

1. download PDF or DOCX and send it by email themselves;
2. download/print the document and send it through a post office themselves;
3. print the document and deliver it through another user-controlled method.

JanaVani does not perform any of these external delivery actions.

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
    +----> User sends email
    |
    +----> User prints and posts
    |
    +----> User prints and delivers
```

The last three actions are outside JanaVani's execution boundary.

## Prohibited behavior

No JanaVani surface or service may:

- send the generated document by email;
- call an SMTP/email delivery service to transmit the document;
- submit the document to a government portal automatically;
- send the document to an office's email address;
- mail or courier the document on the user's behalf;
- interpret a generated/downloaded artifact as a government submission;
- claim government receipt or acknowledgement merely because a document was generated.

## Address and email handling

The document may contain verified `To` and `CC` address/email information so
the user can review it and use it for their own delivery. This information is
**document metadata, not a delivery instruction to JanaVani**.

The user must be able to correct the document and destination details before
download.

## Lifecycle boundary

`DOCUMENT_GENERATED` and `DOCUMENT_DOWNLOADED` are user-facing artifact events.
They do not advance a CivicCase to `SUBMITTED` or `ACKNOWLEDGED`.

The CivicCase submission lifecycle remains a domain model for future
capability evolution, but no current JanaVani adapter may perform external
submission automatically.

## Enforcement

Document-generation tests should verify that the generation path has no email
or external-submission side effect. Any future transport integration that
could transmit documents must be rejected unless this policy is explicitly
changed at the product-governance level.
