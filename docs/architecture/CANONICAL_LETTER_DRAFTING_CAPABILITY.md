# Canonical Letter Drafting Capability

## Status

Implemented as a shared Case → Authority → Document capability and extended by a
non-persistent template-first preview workflow consumed by the WebApp and Telegram
surfaces. The surfaces must not implement independent letter-composition engines.

## Boundaries

- `src/capabilities/letter_drafting.py` owns structured citizen inputs and canonical
  document composition over an owned Case and verified Authority.
- `src/documents/template_models.py` owns template value objects; `src/documents/template_definitions.py`
  contains curated, content-free definitions; `src/documents/template_catalogue.py`
  owns lookup and version resolution for complaint, grievance, RTI, representation,
  petition and administrative evidence-demand formats.
- `src/services/civic_draft_workflow.py` composes a transient preview through those
  templates and optionally requests a validated AI wording proposal.
- `src/services/civic_draft_executor.py` is the remote AI trust boundary. It uses
  the shared AI execution gateway, actual caller identity, capability authorization,
  exact remote-processing scope, and allow-listed model-output validation.
- `src/web/civic_draft_router.py` and the Telegram command/state adapter are transports;
  they do not own legal or template semantics.

These preview routes do not create a Case, persist the citizen's draft, or submit a
document. Case-bound draft persistence and owner-scoped review remain with the
canonical `LetterDraftingCapability` / `DocumentReviewCapability` flow.

## Template and privacy rules

The catalogue stores generic structure, reviewed starter wording, version, purpose,
field names, language, jurisdiction scope and review metadata—not citizen names,
addresses, raw narratives, notice identifiers, evidence, credentials or completed
documents. The administrative evidence-demand format was curated from the supplied
template, with the silence-as-consent and self-executing-legal-effect assertions
reframed as unverified positions rather than default claims.

A user-provided draft may be sent to the remote AI provider only after an explicit
remote-processing action and a verified authenticated identity. For this optional
citizen-facing capability, `civic:ai-draft` is derived only for the current consented
request; it is never persisted to the identity link, account, profile, or future session.
The Telegram drafting journey is restricted to private chats. The model may propose
editable wording; legal citations, deadlines, verified authorities, evidence, and legal
effects are not inferred as facts.

The currently shipped catalogue is a curated source-controlled library. Saving a
citizen-specific custom structure is **not** implemented yet. Any future saved-format
feature must store only a separately reviewed, allow-listed structural model, never a
redacted copy of arbitrary private prose, and must use a durable owner/approval
boundary before it becomes reusable by others.

## Canonical flow

Citizen inputs → template selection → deterministic preview → optional explicit AI
improvement → schema-validated suggested wording → editable citizen review. For a
Case-bound draft, the canonical path remains:

Owned Case + verified Authority → LetterDraftingCapability → DocumentDraft and
evidence/provenance references → citizen review/correction → explicit approval →
separate consequential submission capability, if applicable.

## Required gates

Case ownership for Case-bound drafts; verified destinations where applicable; source
provenance for factual/legal claims; explicit remote-processing consent; allow-listed
AI output; editable citizen review; no submission from generation/rendering; and no
promotion of private text into shared templates or AI training by default.
