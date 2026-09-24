# Canonical Letter Drafting Capability

## Status

Implemented as a shared capability over the canonical Case → Authority → Document
path. It is not a WebApp or Telegram feature.

## Boundary

src/capabilities/letter_drafting.py owns structured citizen letter inputs,
composition, evidence/provenance references, and draft → reviewed → approved
state.

It does not own HTTP or Telegram transport, identity authentication,
authorization implementation, authority verification, evidence storage,
renderer internals, external submission, delivery, or legal determination.

## Source template

The reusable source format is:
docs/templates/NOTICE_NON_CONSENT_CONDITIONAL_ACCEPTANCE_RESOLUTION.md

User-position language such as non-consent, conditional acceptance, requests for
resolution, response periods, reservations and legal-framework references is
preserved as input. The capability does not turn a stated position into an
automatically established legal effect.

Jurisdiction-specific legal citations must be supplied or verified by the
appropriate authority/evidence workflow. They are not silently invented or
injected.

## Canonical flow

Citizen input → owned Case + verified Authority → LetterDraftingCapability →
DocumentDraft + evidence/provenance references → citizen review/correction →
explicit approval → consequential submission capability, if applicable.

## Surface rule

WebApp, Telegram, Android, iOS, WhatsApp, Messenger and future surfaces consume
this capability rather than implementing independent letter composition.

## Separation rule

Letter composition is separate from rendering because rendering is an
independent provider boundary. Approval remains with the drafting capability
because it is part of the document review state; splitting it would create
duplicated orchestration.

## Required gates

Case ownership, verified destination, evidence/provenance references, explicit
review, explicit approval, and no submission from the rendering path.
