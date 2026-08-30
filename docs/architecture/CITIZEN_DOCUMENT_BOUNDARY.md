# Citizen Document Delivery Boundary

## Canonical product rule

JanaVani's responsibility ends when it delivers the citizen's final civic document in the format the citizen selected:

- PDF
- editable Word/DOCX document

Everything after delivery is outside JanaVani's business responsibility.

## JanaVani does NOT ask or decide

JanaVani must not add workflow choices or UI prompts for:

- Print & Post
- Send by Email
- Keep for Later
- Postal submission
- Email submission
- Any other external submission channel

The citizen may independently print, email, post, upload, archive, or otherwise use the delivered file. Those actions are outside the JanaVani product boundary.

## Canonical flow

```text
Citizen problem
  -> Issue Understanding
  -> Authority Discovery / Verification
  -> Case
  -> Evidence / Public Sources
  -> Document Preparation
  -> Citizen Review / Correction
  -> Final Document
  -> Citizen chooses PDF or DOCX
  -> JanaVani delivers the file
  -> END OF JANAVANI RESPONSIBILITY
```

## Security and privacy

Document rendering must not fetch additional personal or sensitive information, query unrelated databases, email the document, or submit it to an authority. The renderer receives the reviewed document draft and produces the selected artifact.

## Shared infrastructure rule

This boundary is channel-neutral. Telegram, Telegram Mini App, WebApp, Mobile and future access surfaces all use the same document preparation and rendering capabilities. A channel may provide its native file-delivery mechanism, but it must not introduce external-submission workflow semantics into the shared core.
